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
  ALLOWED_ORIGINS                      origini ammesse, separate da virgola (ammesso "https://*.dominio");
                                       sempre ammesse anche https://$RAILWAY_PUBLIC_DOMAIN e l'origine uguale all'Host
  VOICE_MAX_PER_HOUR (default 60), CONTACT_MAX_PER_HOUR (default 30)
                                       tetti globali (tutti i visitatori insieme): limitano il costo di un abuso
                                       distribuito su molti indirizzi

Sicurezza (in breve):
  - l'IP del visitatore arriva solo da X-Real-IP, che nginx riscrive sempre (vedi nginx.conf); IPv6 contato per /64;
  - limiti per IP, per destinatario della conferma e globali, con memoria limitata;
  - nessun campo a riga singola può contenere a capo o caratteri di controllo/invisibili (niente header injection);
  - tutto ciò che va nell'HTML delle e-mail è escapato; la conferma al visitatore non ripete il suo messaggio
    (altrimenti il modulo servirebbe a mandare testo arbitrario a indirizzi altrui dal nostro dominio);
  - errori: risposte JSON generiche, nei log solo il tipo di eccezione.

Nei log: solo esito e canale, mai dati personali.
"""
import base64
import collections
import hashlib
import hmac
import html
import ipaddress
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
# Niente '*.up.railway.app': è un dominio condiviso, chiunque vi pubblica un'app. Il dominio Railway del servizio
# arriva da RAILWAY_PUBLIC_DOMAIN (impostata da Railway) o dall'Host della richiesta.
DEFAULT_ORIGINS = ('https://odyrasystemautomation.it', 'https://www.odyrasystemautomation.it')
DEFAULT_FROM = 'Odyra <noreply@odyrasystemautomation.it>'
DEFAULT_TO = 'team@odyrasystemautomation.it'
VOICE_LANGS = ('it', 'en', 'es', 'fr', 'de', 'pl', 'ro')
VOICE_TTL = 10 * 60  # il token serve solo a entrare; LiveKit poi lo rinnova da sé per la durata della chiamata
SOCKET_TIMEOUT = 15  # secondi: una connessione lenta o muta non tiene occupato un thread
# Caratteri di controllo C0/C1 (tranne a capo e tab), separatori di riga Unicode, controlli bidirezionali e caratteri
# a larghezza zero: mai utili in un modulo, utili per header injection o per mascherare testo.
BAD_CHARS = re.compile('[\x00-\x08\x0b-\x1f\x7f-\x9f\u200b-\u200f\u2028-\u202e\u2060-\u2069\ufeff]')
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
    railway = env('RAILWAY_PUBLIC_DOMAIN').lower()
    if railway and re.fullmatch(r'[a-z0-9.-]+', railway):
        items.append('https://' + railway)
    return [x for x in items if x]


def origin_ok(headers):
    """L'Origin (o, se manca, l'origine del Referer) deve essere tra quelle ammesse, o avere lo stesso host
    della richiesta (stessa origine: un browser non può mandare un Host diverso da quello del sito che chiama)."""
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
    host_hdr = (headers.get('Host') or '').strip().lower()
    if host_hdr and p.netloc == host_hdr and (p.scheme == 'https' or p.hostname in ('localhost', '127.0.0.1')):
        return True
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
    """Finestra scorrevole per chiave, con memoria limitata: al massimo max_keys chiavi. Le chiavi sono tenute in
    ordine di ultimo uso, quindi la pulizia delle scadute e lo sfratto delle più vecchie costano O(1) ammortizzato
    (prima la pulizia scorreva tutto il dizionario a ogni richiesta, oltre 10000 chiavi)."""

    def __init__(self, limit=5, window=600, max_keys=20000):
        self.limit, self.window, self.max_keys = limit, window, max_keys
        self.hits = collections.OrderedDict()
        self.lock = threading.Lock()

    def allow(self, key, now=None):
        now = time.monotonic() if now is None else now
        with self.lock:
            # chiavi in testa = usate meno di recente: si tolgono finché sono scadute
            while self.hits:
                k, q = next(iter(self.hits.items()))
                if q and now - q[-1] < self.window:
                    break
                del self.hits[k]
            q = self.hits.get(key)
            if q is None:
                q = self.hits[key] = collections.deque()
            self.hits.move_to_end(key)
            while q and now - q[0] >= self.window:
                q.popleft()
            if len(q) >= self.limit:
                return False
            q.append(now)
            while len(self.hits) > self.max_keys:  # troppe chiavi attive: si sfratta la meno recente
                self.hits.popitem(last=False)
            return True

    def reset(self):
        with self.lock:
            self.hits.clear()


LIMIT_CONTACT = RateLimiter(5, 600)        # per IP: 5 invii in 10 minuti
LIMIT_CONFIRM = RateLimiter(2, 86400)      # per destinatario: 2 conferme al giorno allo stesso indirizzo
LIMIT_VOICE = RateLimiter(5, 600)          # per IP: 5 token in 10 minuti
LIMIT_VOICE_DAY = RateLimiter(20, 86400)   # per IP: 20 token al giorno
LIMIT_GLOBAL = RateLimiter(10 ** 6, 3600)  # tetti globali orari: chiavi 'voce' e 'contatto', limite letto dall'env


def global_allow(kind, now=None):
    """Tetto orario per tutti i visitatori insieme (VOICE_MAX_PER_HOUR / CONTACT_MAX_PER_HOUR)."""
    name, default = {'voce': ('VOICE_MAX_PER_HOUR', 60), 'contatto': ('CONTACT_MAX_PER_HOUR', 30)}[kind]
    try:
        limit = max(0, int(env(name, str(default))))
    except ValueError:
        limit = default
    now = time.monotonic() if now is None else now
    with LIMIT_GLOBAL.lock:
        q = LIMIT_GLOBAL.hits.setdefault(kind, collections.deque())
        while q and now - q[0] >= LIMIT_GLOBAL.window:
            q.popleft()
        if len(q) >= limit:
            return False
        q.append(now)
        return True


def reset_limits():
    for rl in (LIMIT_CONTACT, LIMIT_CONFIRM, LIMIT_VOICE, LIMIT_VOICE_DAY, LIMIT_GLOBAL):
        rl.reset()


def ip_key(value, fallback):
    """Chiave del limite per un indirizzo: IPv4 intero, IPv6 per rete /64 (un utente IPv6 ne ha di solito
    un'intera /64 e potrebbe cambiare indirizzo a ogni richiesta). Valori non validi: l'indirizzo della connessione."""
    for v in (value, fallback):
        try:
            ip = ipaddress.ip_address((v or '').strip())
        except ValueError:
            continue
        if ip.version == 6 and ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        if ip.version == 6:
            return str(ipaddress.ip_network(f'{ip}/64', strict=False))
        return str(ip)
    return 'sconosciuto'


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
        'exp': now + VOICE_TTL,
        'name': 'Visitatore',
        # Solo entrare nella propria stanza, pubblicare il microfono e ascoltare. Niente dati verso la stanza,
        # niente video o schermo, niente metadati propri, nessun permesso di amministrazione, creazione o elenco.
        'video': {'roomJoin': True, 'room': room, 'canPublish': True, 'canPublishSources': ['microphone'],
                  'canSubscribe': True, 'canPublishData': False, 'canUpdateOwnMetadata': False},
        # Stanza usa e getta: si chiude poco dopo che resta vuota, al massimo visitatore + agente (+1 di margine).
        # I metadati dell'agente sono costruiti qui, da una lingua in whitelist: il browser non li sceglie.
        'roomConfig': {'emptyTimeout': 30, 'departureTimeout': 10, 'maxParticipants': 3,
                       'agents': [{'agentName': env('VOICE_AGENT_NAME', 'odyra_web'), 'metadata': json.dumps({'lang': lang})}]},
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
    v = v.replace('\r\n', '\n').replace('\r', '\n').replace('\x85', '\n').strip()
    # niente caratteri di controllo, separatori di riga Unicode, controlli bidi, larghezza zero (restano a capo e tab)
    return BAD_CHARS.sub('', v).strip()


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
        if '\n' in lead[field] or '\t' in lead[field]:
            raise Invalid(field)
    if not email_ok(lead['email']):
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


def email_ok(addr):
    """Indirizzo semplice e sicuro da mettere in To/Reply-To: niente nomi, virgolette, spazi o più indirizzi."""
    if len(addr) > 254 or not EMAIL_RE.fullmatch(addr):
        return False
    local = addr.rsplit('@', 1)[0]
    return len(local) <= 64 and not local.startswith('.') and not local.endswith('.') and '..' not in local


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


def greeting_name(name):
    """Primo nome per il saluto, solo se sembra un nome (lettere, apostrofo, trattino; max 30 caratteri).
    Altrimenti saluto generico: il campo nome non deve poter portare link o testo a indirizzi altrui."""
    first = name.split()[0] if name.split() else ''
    return first if re.fullmatch(r"[^\W\d_](?:[^\W\d_]|['’-]){0,29}", first) else ''


def visitor_email(lead):
    # Non ripete il messaggio del visitatore: chiunque può scrivere qualunque indirizzo nel modulo, e una conferma
    # con testo scelto da chi invia farebbe del sito un ripetitore di spam con il nostro dominio come mittente.
    first = greeting_name(lead['name'])
    hello = f'Ciao {first},' if first else 'Ciao,'
    text = (f'{hello}\n\nabbiamo ricevuto la tua richiesta. Ti rispondiamo entro un giorno lavorativo.\n\n'
            'Se non sei stato tu a scriverci, ignora questa e-mail.\n\nIl team Odyra\n' + SITE)
    inner = (f'<p style="font-size:15px;line-height:1.6">{html.escape(hello)}</p>'
             '<p style="font-size:15px;line-height:1.6">abbiamo ricevuto la tua richiesta. Ti rispondiamo entro un giorno lavorativo.</p>'
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
    url = env('LEAD_WEBHOOK_URL')
    if urllib.parse.urlsplit(url).scheme not in ('https', 'http'):  # mai file:, ftp: e simili
        raise RuntimeError('schema non ammesso')
    payload = dict(lead, source='odyra_website_form', form=lead.get('source', ''),
                   submitted_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    req = urllib.request.Request(url, data=json.dumps(payload, ensure_ascii=False).encode(), method='POST',
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
                if LIMIT_CONFIRM.allow(lead['email'].lower()):
                    send_mail(lead['email'], *visitor_email(lead))
                    log.info('contatto: conferma al visitatore inviata (%s)', ch)
                else:
                    log.info('contatto: conferma al visitatore non inviata (limite per destinatario)')
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
    timeout = SOCKET_TIMEOUT  # timeout del socket: letture e scritture bloccate non durano per sempre

    def version_string(self):  # solo il nome, senza versione di Python
        return self.server_version

    def log_message(self, fmt, *args):  # niente IP né indirizzi completi nei log di accesso
        pass

    def log_error(self, fmt, *args):  # errori di protocollo: solo il formato, senza IP né contenuti
        log.info('http: %s', fmt.split(' ')[0])

    def client_ip(self):
        """Chiave del limite per il visitatore. Solo X-Real-IP, che nginx riscrive sempre con l'indirizzo che il
        proxy di Railway ha visto (mai il primo valore di X-Forwarded-For, che il client può inventare)."""
        return ip_key(self.headers.get('X-Real-IP'), self.client_address[0])

    def send_error(self, code, message=None, explain=None):
        """Errori generati da http.server (metodo sconosciuto, richiesta malformata...): JSON, senza pagina HTML."""
        self.close_connection = True
        try:
            self.reply(code, {'error': 'metodo' if code == 501 else 'richiesta' if code < 500 else 'errore_interno'})
        except Exception:
            pass

    def reply(self, status, obj, allow=None):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        if status == 429:
            self.send_header('Retry-After', '600')
        if allow:
            self.send_header('Allow', allow)
        if self.close_connection:
            self.send_header('Connection', 'close')
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)

    def read_json(self):
        """Controlli comuni dei POST. Restituisce (dati, None) o (None, (stato, errore))."""
        ctype = (self.headers.get('Content-Type') or '').split(';')[0].strip().lower()
        if ctype != 'application/json':
            return None, (415, 'content_type')
        if self.headers.get('Transfer-Encoding'):  # nginx manda sempre Content-Length; chunked qui non serve
            return None, (411, 'lunghezza')
        try:
            length = int(self.headers.get('Content-Length') or '-1')
        except ValueError:
            length = -1
        if length < 0:
            return None, (411, 'lunghezza')
        if length > MAX_BODY:
            return None, (413, 'troppo_grande')
        try:
            raw = self.rfile.read(length)
        except OSError:  # compreso il timeout del socket: il client ha dichiarato più byte di quanti ne manda
            return None, (408, 'timeout')
        if not origin_ok(self.headers):
            return None, (403, 'origine')
        if len(raw) != length:  # corpo più corto del Content-Length dichiarato (connessione chiusa o timeout)
            return None, (400, 'lunghezza')
        try:
            return json.loads(raw.decode('utf-8') or 'null'), None
        except (UnicodeDecodeError, ValueError, RecursionError):  # RecursionError: JSON annidato a migliaia di livelli
            return None, (400, 'json')

    POST_ROUTES = ('/api/contatto', '/api/voce/token')

    def guarded(self, fn):
        """Qualunque eccezione imprevista diventa un 500 generico: niente stack nella risposta, solo il tipo nei log."""
        try:
            return fn()
        except Exception as ex:  # noqa: BLE001
            log.error('errore interno: %s', type(ex).__name__)
            self.close_connection = True
            try:
                self.reply(500, {'error': 'errore_interno'})
            except Exception:
                pass

    def do_GET(self):
        self.guarded(self.get)

    def get(self):
        route = self.path.split('?')[0]
        if route == '/api/salute':
            ch = email_channel()
            webhook = bool(env('LEAD_WEBHOOK_URL'))
            return self.reply(200, {'ok': True, 'contatto': bool(ch or webhook), 'email': ch, 'webhook': webhook,
                                    'voce': voice_configured()})
        if route in self.POST_ROUTES:
            return self.reply(405, {'error': 'metodo'}, allow='POST')
        self.reply(404, {'error': 'non_trovato'})

    def do_HEAD(self):
        self.reply(405, {'error': 'metodo'}, allow='GET, POST')

    def not_allowed(self):
        self.close_connection = True
        self.reply(405, {'error': 'metodo'}, allow='GET, POST')

    do_PUT = do_DELETE = do_PATCH = do_OPTIONS = do_TRACE = do_CONNECT = not_allowed

    def do_POST(self):
        self.guarded(self.post)

    def post(self):
        route = self.path.split('?')[0]
        if route == '/api/contatto':
            return self.contatto()
        if route == '/api/voce/token':
            return self.voce()
        self.close_connection = True  # il corpo non è stato letto
        self.reply(404, {'error': 'non_trovato'})

    def contatto(self):
        data, err = self.read_json()
        if err:
            self.close_connection = True  # il corpo potrebbe non essere stato letto
            return self.reply(err[0], {'error': err[1]})
        if not LIMIT_CONTACT.allow(self.client_ip()) or not global_allow('contatto'):
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
        ip = self.client_ip()
        if not LIMIT_VOICE.allow(ip) or not LIMIT_VOICE_DAY.allow(ip) or not global_allow('voce'):
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
