#!/usr/bin/env python3
"""Piccolo server delle API del sito Odyra, dietro nginx. Solo libreria standard.

  POST /api/contatto     modulo contatti: e-mail al team + conferma al visitatore, webhook facoltativo
  POST /api/voce/token   token per la demo vocale nel browser (JWT HS256, 15 minuti)
  GET  /api/salute       stato e canali configurati (senza valori)

Ascolta su 127.0.0.1:8090 (API_HOST / API_PORT). Configurazione solo da variabili d'ambiente,
lette a ogni richiesta (così un cambio di variabili su Railway vale al riavvio del container):

  RESEND_API_KEY                       e-mail tramite API HTTP (ha la precedenza)
  SMTP_HOST, SMTP_PORT (587 STARTTLS, 465 SSL), SMTP_USER, SMTP_PASSWORD
                                       e-mail tramite SMTP, se manca la chiave API
  MAIL_FROM (default "Odyra <noreply@odyrasystemautomation.it>"), MAIL_TO (default team@odyrasystemautomation.it)
  LEAD_WEBHOOK_URL                     facoltativo: POST JSON del lead
  LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET, VOICE_AGENT_NAME (default odyra_web)
  ALLOWED_ORIGINS                      origini ammesse, separate da virgola (ammesso "https://*.dominio")

Nei log: solo esito e canale, mai dati personali.
"""
import base64
import collections
import hashlib
import hmac
import html
import json
import logging
import os
import re
import secrets
import smtplib
import ssl
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from email.message import EmailMessage
from email.utils import formataddr, make_msgid, formatdate
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

log = logging.getLogger('odyra-api')

MAX_BODY = 16 * 1024
TIMEOUT = 10
SITE = 'https://odyrasystemautomation.it'
LOGO = SITE + '/assets/logos/odyra-mark.png'
DEFAULT_ORIGINS = ('https://odyrasystemautomation.it', 'https://www.odyrasystemautomation.it', 'https://*.up.railway.app')
DEFAULT_FROM = 'Odyra <noreply@odyrasystemautomation.it>'
DEFAULT_TO = 'team@odyrasystemautomation.it'
VOICE_LANGS = ('it', 'en', 'es', 'fr', 'de', 'pl', 'ro')
EMAIL_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$")
# campo: (lunghezza minima, massima)
LIMITS = {'name': (1, 150), 'email': (3, 255), 'company': (0, 200), 'phone': (0, 40), 'need': (0, 2000), 'message': (0, 5000),
          'source': (0, 80), 'page': (0, 300)}
ATTR_KEYS = ('gclid', 'wbraid', 'gbraid', 'msclkid', 'campaignid', 'adgroupid', 'keyword', 'matchtype', 'network', 'device',
             'creative', 'placement', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
             'landing_page', 'referrer', 'first_seen_at')


def env(name, default=''):
    return (os.environ.get(name) or default).strip()


# ───────── configurazione ─────────
def email_channel():
    """'api', 'smtp' o None: quale canale e-mail è configurato (l'API ha la precedenza)."""
    if env('RESEND_API_KEY'):
        return 'api'
    if env('SMTP_HOST'):
        return 'smtp'
    return None


def voice_configured():
    return all(env(k) for k in ('LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET'))


def allowed_origins():
    raw = env('ALLOWED_ORIGINS')
    items = [x.strip().rstrip('/').lower() for x in raw.split(',')] if raw else list(DEFAULT_ORIGINS)
    return [x for x in items if x]


def origin_ok(headers):
    """L'Origin (o, se manca, l'origine del Referer) deve essere tra quelle ammesse."""
    origin = (headers.get('Origin') or '').strip()
    if not origin or origin == 'null':
        ref = (headers.get('Referer') or '').strip()
        if not ref:
            return False
        p = urllib.parse.urlsplit(ref)
        if not p.scheme or not p.netloc:
            return False
        origin = f'{p.scheme}://{p.netloc}'
    origin = origin.rstrip('/').lower()
    p = urllib.parse.urlsplit(origin)
    if p.scheme not in ('http', 'https') or not p.hostname:
        return False
    for allowed in allowed_origins():
        if allowed == origin:
            return True
        if '://*.' in allowed:
            scheme, suffix = allowed.split('://*.', 1)
            host = origin.split('://', 1)[1]
            if p.scheme == scheme and host.endswith('.' + suffix) and len(host) > len(suffix) + 1:
                return True
    return False


# ───────── limite di richieste per IP ─────────
class RateLimiter:
    def __init__(self, limit=5, window=600):
        self.limit, self.window = limit, window
        self.hits = collections.defaultdict(collections.deque)
        self.lock = threading.Lock()

    def allow(self, key, now=None):
        now = time.monotonic() if now is None else now
        with self.lock:
            q = self.hits[key]
            while q and now - q[0] >= self.window:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(now)
            if len(self.hits) > 10000:  # pulizia: chiavi senza richieste recenti
                for k in [k for k, v in self.hits.items() if not v or now - v[-1] >= self.window]:
                    del self.hits[k]
            return True

    def reset(self):
        with self.lock:
            self.hits.clear()


LIMIT_CONTACT = RateLimiter(5, 600)
LIMIT_VOICE = RateLimiter(5, 600)


# ───────── JWT HS256 per la demo vocale ─────────
def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


def jwt_hs256(claims, secret):
    header = {'alg': 'HS256', 'typ': 'JWT'}
    seg = b64url(json.dumps(header, separators=(',', ':')).encode()) + '.' + b64url(json.dumps(claims, separators=(',', ':')).encode())
    sig = hmac.new(secret.encode(), seg.encode('ascii'), hashlib.sha256).digest()
    return seg + '.' + b64url(sig)


def voice_token(lang):
    lang = (lang or 'it').lower() if isinstance(lang, str) else 'it'
    if lang not in VOICE_LANGS:
        lang = 'it'
    key, secret = env('LIVEKIT_API_KEY'), env('LIVEKIT_API_SECRET')
    room = f'odyra-web-{uuid.uuid4()}'
    now = int(time.time())
    claims = {
        'iss': key,
        'sub': f'visitor-{secrets.token_hex(4)}',
        'iat': now,
        'nbf': now,
        'exp': now + 15 * 60,
        'name': 'Visitatore',
        'video': {'roomJoin': True, 'room': room, 'canPublish': True, 'canSubscribe': True, 'canPublishData': True},
        'roomConfig': {'agents': [{'agentName': env('VOICE_AGENT_NAME', 'odyra_web'), 'metadata': json.dumps({'lang': lang})}]},
    }
    return {'token': jwt_hs256(claims, secret), 'url': env('LIVEKIT_URL'), 'room': room, 'lang': lang}


# ───────── modulo contatti ─────────
class Invalid(Exception):
    pass


def clean(v):
    if v is None:
        return ''
    if not isinstance(v, str):
        raise Invalid('tipo')
    v = v.replace('\r\n', '\n').replace('\r', '\n').strip()
    # niente caratteri di controllo (tranne a capo e tab)
    return re.sub(r'[\x00-\x08\x0b-\x1f\x7f]', '', v)


def validate_lead(data):
    """Restituisce il lead pulito o solleva Invalid(campo)."""
    if not isinstance(data, dict):
        raise Invalid('json')
    lead = {}
    for field, (lo, hi) in LIMITS.items():
        v = clean(data.get(field))
        if len(v) < lo or len(v) > hi:
            raise Invalid(field)
        lead[field] = v
    for field in ('name', 'email', 'company', 'phone', 'source', 'page'):
        if '\n' in lead[field]:
            raise Invalid(field)
    if not EMAIL_RE.match(lead['email']):
        raise Invalid('email')
    if lead['phone'] and not re.fullmatch(r'[0-9+()./\s-]{4,40}', lead['phone']):
        raise Invalid('phone')
    if not (lead['message'] or lead['need']):
        raise Invalid('message')
    if data.get('privacy') is not True:
        raise Invalid('privacy')
    attr = data.get('attribution') or {}
    if not isinstance(attr, dict):
        raise Invalid('attribution')
    lead['attribution'] = {k: clean(attr[k])[:300].replace('\n', ' ') for k in ATTR_KEYS if isinstance(attr.get(k), str) and attr[k].strip()}
    return lead


def is_spam(data):
    return isinstance(data, dict) and bool(str(data.get('website') or '').strip())


LABELS = [('name', 'Nome'), ('company', 'Azienda'), ('email', 'E-mail'), ('phone', 'Telefono'), ('need', 'Esigenza'),
          ('message', 'Messaggio'), ('source', 'Modulo'), ('page', 'Pagina')]


def _wrap(title, inner):
    return f'''<!doctype html><html lang="it"><body style="margin:0;padding:0;background:#f3f5f9">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f3f5f9;padding:24px 0"><tr><td align="center">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:8px;overflow:hidden;font-family:Arial,Helvetica,sans-serif;color:#0b1b33">
<tr><td style="background:#071A3A;padding:20px 28px"><img src="{LOGO}" width="36" height="36" alt="Odyra" style="vertical-align:middle;border:0"> <span style="color:#ffffff;font-size:18px;font-weight:bold;vertical-align:middle;margin-left:8px">Odyra System</span></td></tr>
<tr><td style="padding:28px"><h1 style="font-size:20px;margin:0 0 16px">{html.escape(title)}</h1>{inner}</td></tr>
<tr><td style="padding:16px 28px;border-top:1px solid #e3e8f0;font-size:12px;color:#5b6b82">Odyra System · Verypos S.r.l. · Viale Papiniano 8, 20123 Milano · <a href="{SITE}" style="color:#5b6b82">odyrasystemautomation.it</a></td></tr>
</table></td></tr></table></body></html>'''


def _rows(pairs):
    return ''.join(f'<tr><td style="padding:6px 12px 6px 0;color:#5b6b82;vertical-align:top;white-space:nowrap">{html.escape(k)}</td>'
                   f'<td style="padding:6px 0;white-space:pre-wrap">{html.escape(v)}</td></tr>' for k, v in pairs if v)


def team_email(lead):
    pairs = [(label, lead[k]) for k, label in LABELS]
    attr = list(lead['attribution'].items())
    text = '\n'.join(f'{label}: {v}' for label, v in pairs if v)
    inner = f'<table role="presentation" cellpadding="0" cellspacing="0" style="font-size:14px;line-height:1.5">{_rows(pairs)}</table>'
    if attr:
        text += '\n\n--- Provenienza ---\n' + '\n'.join(f'- {k}: {v}' for k, v in attr)
        inner += ('<h2 style="font-size:14px;margin:24px 0 8px;color:#5b6b82">Provenienza</h2>'
                  f'<table role="presentation" cellpadding="0" cellspacing="0" style="font-size:12px;line-height:1.5;color:#5b6b82">{_rows(attr)}</table>')
    subject = f'Nuova richiesta dal sito: {lead["name"]}' + (f' ({lead["company"]})' if lead['company'] else '')
    return subject[:200], text, _wrap('Nuova richiesta dal sito', inner)


def visitor_email(lead):
    first = lead['name'].split()[0] if lead['name'].split() else lead['name']
    text = (f'Ciao {first},\n\nabbiamo ricevuto la tua richiesta. Ti rispondiamo entro un giorno lavorativo.\n\n'
            f'Il tuo messaggio:\n{lead["message"] or lead["need"]}\n\n'
            'Se non sei stato tu a scriverci, ignora questa e-mail.\n\nIl team Odyra\n' + SITE)
    inner = (f'<p style="font-size:15px;line-height:1.6">Ciao {html.escape(first)},</p>'
             '<p style="font-size:15px;line-height:1.6">abbiamo ricevuto la tua richiesta. Ti rispondiamo entro un giorno lavorativo.</p>'
             '<p style="font-size:13px;color:#5b6b82;margin:20px 0 6px">Il tuo messaggio</p>'
             f'<p style="font-size:14px;line-height:1.6;white-space:pre-wrap;background:#f3f5f9;padding:12px 14px;border-radius:6px">{html.escape(lead["message"] or lead["need"])}</p>'
             '<p style="font-size:13px;color:#5b6b82;line-height:1.6">Se non sei stato tu a scriverci, ignora questa e-mail.</p>'
             '<p style="font-size:15px;line-height:1.6">Il team Odyra</p>')
    return 'Abbiamo ricevuto la tua richiesta | Odyra', text, _wrap('Grazie, abbiamo ricevuto la tua richiesta', inner)


def send_api(to, subject, text, body_html, reply_to=None):
    payload = {'from': env('MAIL_FROM', DEFAULT_FROM), 'to': [to], 'subject': subject, 'text': text, 'html': body_html}
    if reply_to:
        payload['reply_to'] = reply_to
    req = urllib.request.Request('https://api.resend.com/emails', data=json.dumps(payload).encode(), method='POST',
                                 headers={'Authorization': 'Bearer ' + env('RESEND_API_KEY'), 'Content-Type': 'application/json',
                                          'User-Agent': 'odyra-site/1'})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        if r.status >= 300:
            raise RuntimeError(f'status {r.status}')


def send_smtp(to, subject, text, body_html, reply_to=None):
    msg = EmailMessage()
    sender = env('MAIL_FROM', DEFAULT_FROM)
    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = subject
    msg['Date'] = formatdate(localtime=False)
    msg['Message-ID'] = make_msgid(domain='odyrasystemautomation.it')
    if reply_to:
        msg['Reply-To'] = reply_to
    msg.set_content(text)
    msg.add_alternative(body_html, subtype='html')
    host, port = env('SMTP_HOST'), int(env('SMTP_PORT', '587') or 587)
    user, password = env('SMTP_USER'), env('SMTP_PASSWORD')
    ctx = ssl.create_default_context()
    if port == 465:
        conn = smtplib.SMTP_SSL(host, port, timeout=TIMEOUT, context=ctx)
    else:
        conn = smtplib.SMTP(host, port, timeout=TIMEOUT)
    try:
        conn.ehlo()
        if port != 465:
            if conn.has_extn('starttls'):
                conn.starttls(context=ctx)
                conn.ehlo()
            elif user:
                raise RuntimeError('STARTTLS non disponibile')  # mai credenziali in chiaro
        if user:
            conn.login(user, password)
        conn.send_message(msg)
    finally:
        try:
            conn.quit()
        except Exception:
            conn.close()


def send_mail(*args, **kw):
    ch = email_channel()
    return (send_api if ch == 'api' else send_smtp)(*args, **kw)


def send_webhook(lead):
    payload = dict(lead, source='odyra_website_form', form=lead.get('source', ''),
                   submitted_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    req = urllib.request.Request(env('LEAD_WEBHOOK_URL'), data=json.dumps(payload, ensure_ascii=False).encode(), method='POST',
                                 headers={'Content-Type': 'application/json', 'User-Agent': 'odyra-site/1'})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        if r.status >= 300:
            raise RuntimeError(f'status {r.status}')


def deliver(lead):
    """Invia il lead su tutti i canali configurati. Restituisce (configurati, riusciti)."""
    done, configured = [], []
    ch = email_channel()
    if ch:
        configured.append('email')
        try:
            subject, text, body = team_email(lead)
            send_mail(env('MAIL_TO', DEFAULT_TO), subject, text, body, reply_to=lead['email'])
            done.append('email')
            log.info('contatto: e-mail al team inviata (%s)', ch)
            try:
                send_mail(lead['email'], *visitor_email(lead))
                log.info('contatto: conferma al visitatore inviata (%s)', ch)
            except Exception as ex:
                log.warning('contatto: conferma al visitatore non inviata (%s): %s', ch, type(ex).__name__)
        except Exception as ex:
            log.warning('contatto: e-mail al team non inviata (%s): %s', ch, type(ex).__name__)
    if env('LEAD_WEBHOOK_URL'):
        configured.append('webhook')
        try:
            send_webhook(lead)
            done.append('webhook')
            log.info('contatto: webhook inviato')
        except Exception as ex:
            log.warning('contatto: webhook non riuscito: %s', type(ex).__name__)
    return configured, done


# ───────── HTTP ─────────
class Handler(BaseHTTPRequestHandler):
    server_version = 'odyra-api'
    sys_version = ''
    protocol_version = 'HTTP/1.1'

    def log_message(self, fmt, *args):  # niente IP né indirizzi completi nei log di accesso
        pass

    def client_ip(self):
        xff = self.headers.get('X-Forwarded-For') or ''
        first = xff.split(',')[0].strip()
        return first or self.client_address[0]

    def reply(self, status, obj):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        if status == 429:
            self.send_header('Retry-After', '600')
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        """Controlli comuni dei POST. Restituisce (dati, None) o (None, (stato, errore))."""
        ctype = (self.headers.get('Content-Type') or '').split(';')[0].strip().lower()
        if ctype != 'application/json':
            return None, (415, 'content_type')
        try:
            length = int(self.headers.get('Content-Length') or '-1')
        except ValueError:
            length = -1
        if length < 0:
            return None, (411, 'lunghezza')
        if length > MAX_BODY:
            return None, (413, 'troppo_grande')
        raw = self.rfile.read(length)
        if not origin_ok(self.headers):
            return None, (403, 'origine')
        try:
            return json.loads(raw.decode('utf-8') or 'null'), None
        except (UnicodeDecodeError, ValueError):
            return None, (400, 'json')

    def do_GET(self):
        if self.path.split('?')[0] == '/api/salute':
            ch = email_channel()
            webhook = bool(env('LEAD_WEBHOOK_URL'))
            return self.reply(200, {'ok': True, 'contatto': bool(ch or webhook), 'email': ch, 'webhook': webhook,
                                    'voce': voice_configured()})
        self.reply(404, {'error': 'non_trovato'})

    def do_HEAD(self):
        self.reply(405, {'error': 'metodo'})

    def do_POST(self):
        route = self.path.split('?')[0]
        if route == '/api/contatto':
            return self.contatto()
        if route == '/api/voce/token':
            return self.voce()
        self.reply(404, {'error': 'non_trovato'})

    def contatto(self):
        data, err = self.read_json()
        if err:
            self.close_connection = True  # il corpo potrebbe non essere stato letto
            return self.reply(err[0], {'error': err[1]})
        if not LIMIT_CONTACT.allow(self.client_ip()):
            log.info('contatto: limite di richieste')
            return self.reply(429, {'error': 'troppe_richieste'})
        if is_spam(data):
            log.info('contatto: honeypot, scartato')
            return self.reply(200, {'ok': True})
        try:
            lead = validate_lead(data)
        except Invalid as ex:
            return self.reply(400, {'error': 'non_valido', 'campo': str(ex)})
        configured, done = deliver(lead)
        if not configured:
            log.warning('contatto: nessun canale configurato')
            return self.reply(503, {'error': 'non_configurato'})
        if not done:
            return self.reply(502, {'error': 'invio_non_riuscito'})
        return self.reply(200, {'ok': True})

    def voce(self):
        data, err = self.read_json()
        if err:
            self.close_connection = True  # il corpo potrebbe non essere stato letto
            return self.reply(err[0], {'error': err[1]})
        if not voice_configured():
            return self.reply(503, {'error': 'non_configurato'})
        if not LIMIT_VOICE.allow(self.client_ip()):
            log.info('voce: limite di richieste')
            return self.reply(429, {'error': 'troppe_richieste'})
        lang = data.get('lang') if isinstance(data, dict) else None
        log.info('voce: token emesso')
        return self.reply(200, voice_token(lang))


def make_server(host=None, port=None):
    host = host or env('API_HOST', '127.0.0.1')
    port = int(port if port is not None else env('API_PORT', '8090'))
    srv = ThreadingHTTPServer((host, port), Handler)
    srv.daemon_threads = True
    return srv


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s', stream=sys.stdout)
    srv = make_server()
    ch = email_channel()
    log.info('in ascolto su %s:%s (e-mail: %s, webhook: %s, voce: %s)', *srv.server_address[:2], ch or 'no',
             'sì' if env('LEAD_WEBHOOK_URL') else 'no', 'sì' if voice_configured() else 'no')
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
