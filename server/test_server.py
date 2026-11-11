#!/usr/bin/env python3
"""Test del server delle API. Uso: python3 -m unittest discover -s server -v"""
import base64
import hashlib
import hmac
import http.client
import json
import os
import socket
import socketserver
import sys
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import odyra_server as S  # noqa: E402

ENV_KEYS = ('RESEND_API_KEY', 'SMTP_HOST', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASSWORD', 'MAIL_FROM', 'MAIL_TO', 'LEAD_WEBHOOK_URL',
            'LIVEKIT_URL', 'LIVEKIT_API_KEY', 'LIVEKIT_API_SECRET', 'VOICE_AGENT_NAME', 'ALLOWED_ORIGINS',
            'RAILWAY_PUBLIC_DOMAIN', 'VOICE_MAX_PER_HOUR', 'CONTACT_MAX_PER_HOUR')
ORIGIN = 'https://odyrasystemautomation.it'


def b64d(s):
    return base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))


def lead(**over):
    d = {'name': 'Mario Rossi', 'email': 'mario@example.com', 'company': 'Rossi Srl', 'phone': '+39 333 1234567',
         'need': 'Centralino', 'message': 'Vorrei una demo <b>subito</b>', 'source': 'contatti', 'page': '/contatti',
         'privacy': True, 'website': '', 'attribution': {'gclid': 'abc123', 'utm_source': 'google', 'evil': 'x'}}
    d.update(over)
    return d


class FakeSMTP(socketserver.StreamRequestHandler):
    """Server SMTP minimo, senza STARTTLS né autenticazione: registra i messaggi ricevuti."""
    messages = []

    def handle(self):
        w = lambda s: (self.wfile.write(s.encode() + b'\r\n'), self.wfile.flush())
        w('220 fake ESMTP')
        rcpt, data = [], None
        while True:
            line = self.rfile.readline()
            if not line:
                return
            cmd = line.decode().strip()
            up = cmd.upper()
            if data is not None:
                if cmd == '.':
                    FakeSMTP.messages.append((rcpt, b'\r\n'.join(data).decode()))
                    data, rcpt = None, []
                    w('250 ok')
                else:
                    data.append(line.rstrip(b'\r\n'))
            elif up.startswith('EHLO'):
                self.wfile.write(b'250-fake\r\n250 SIZE 100000\r\n'); self.wfile.flush()
            elif up.startswith('MAIL'):
                w('250 ok')
            elif up.startswith('RCPT'):
                rcpt.append(cmd.split(':', 1)[1].strip()); w('250 ok')
            elif up == 'DATA':
                data = []; w('354 go')
            elif up == 'QUIT':
                w('221 bye'); return
            else:
                w('250 ok')


class Hook(BaseHTTPRequestHandler):
    received = []
    status = 200

    def do_POST(self):
        Hook.received.append(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
        self.send_response(Hook.status); self.send_header('Content-Length', '0'); self.end_headers()

    def log_message(self, *a):
        pass


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = S.make_server('127.0.0.1', 0)
        cls.port = cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown(); cls.srv.server_close()

    def setUp(self):
        self.env = mock.patch.dict(os.environ, {}, clear=False)
        self.env.start()
        for k in ENV_KEYS:
            os.environ.pop(k, None)
        S.reset_limits()

    def tearDown(self):
        self.env.stop()

    def req(self, method, path, body=None, headers=None, ip='203.0.113.7', raw=None):
        h = {'Content-Type': 'application/json', 'Origin': ORIGIN, 'X-Real-IP': ip}
        h.update(headers or {})
        h = {k: v for k, v in h.items() if v is not None}
        c = http.client.HTTPConnection('127.0.0.1', self.port, timeout=15)
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
        c.request(method, path, body=data, headers=h)
        r = c.getresponse()
        out = r.read()
        c.close()
        return r.status, (json.loads(out) if out else None)


class TestHealth(Base):
    def test_unconfigured(self):
        st, b = self.req('GET', '/api/salute')
        self.assertEqual((st, b), (200, {'ok': True, 'contatto': False, 'email': None, 'webhook': False, 'voce': False}))

    def test_configured_no_values(self):
        os.environ.update(SMTP_HOST='smtp.example.com', LIVEKIT_URL='wss://x', LIVEKIT_API_KEY='k', LIVEKIT_API_SECRET='s')
        st, b = self.req('GET', '/api/salute')
        self.assertEqual(b, {'ok': True, 'contatto': True, 'email': 'smtp', 'webhook': False, 'voce': True})
        os.environ['RESEND_API_KEY'] = 're_secret'
        st, b = self.req('GET', '/api/salute')
        self.assertEqual(b['email'], 'api')
        self.assertNotIn('re_secret', json.dumps(b))

    def test_unknown(self):
        self.assertEqual(self.req('GET', '/api/altro')[0], 404)
        self.assertEqual(self.req('POST', '/api/altro', {})[0], 404)


class TestContactRequest(Base):
    def test_503_not_configured(self):
        self.assertEqual(self.req('POST', '/api/contatto', lead()), (503, {'error': 'non_configurato'}))

    def test_content_type(self):
        st, _ = self.req('POST', '/api/contatto', lead(), headers={'Content-Type': 'text/plain'})
        self.assertEqual(st, 415)

    def test_too_large(self):
        st, _ = self.req('POST', '/api/contatto', raw=b'{"a":"' + b'x' * 17000 + b'"}')
        self.assertEqual(st, 413)

    def test_bad_json(self):
        self.assertEqual(self.req('POST', '/api/contatto', raw=b'{nope')[0], 400)

    def test_origin(self):
        self.assertEqual(self.req('POST', '/api/contatto', lead(), headers={'Origin': 'https://evil.example'})[0], 403)
        self.assertEqual(self.req('POST', '/api/contatto', lead(), headers={'Origin': None})[0], 403)
        # senza Origin vale il Referer
        st, _ = self.req('POST', '/api/contatto', lead(), headers={'Origin': None, 'Referer': ORIGIN + '/contatti'})
        self.assertEqual(st, 503)
        # *.up.railway.app non è ammesso di default (dominio condiviso): solo il dominio del servizio
        self.assertEqual(self.req('POST', '/api/contatto', lead(), headers={'Origin': 'https://odyra-production.up.railway.app'})[0], 403)
        os.environ['RAILWAY_PUBLIC_DOMAIN'] = 'odyra-production.up.railway.app'
        self.assertEqual(self.req('POST', '/api/contatto', lead(), headers={'Origin': 'https://odyra-production.up.railway.app'})[0], 503)
        self.assertEqual(self.req('POST', '/api/contatto', lead(), headers={'Origin': 'https://evil.up.railway.app'})[0], 403)
        self.assertEqual(self.req('POST', '/api/contatto', lead(), headers={'Origin': 'https://evilup.railway.app'})[0], 403)
        self.assertEqual(self.req('POST', '/api/contatto', lead(), headers={'Origin': 'http://odyrasystemautomation.it'})[0], 403)

    def test_allowed_origins_env(self):
        os.environ['ALLOWED_ORIGINS'] = 'http://localhost:8080, https://*.example.org'
        self.assertEqual(self.req('POST', '/api/contatto', lead(), headers={'Origin': 'http://localhost:8080'})[0], 503)
        self.assertEqual(self.req('POST', '/api/contatto', lead(), headers={'Origin': 'https://a.example.org'})[0], 503)
        self.assertEqual(self.req('POST', '/api/contatto', lead())[0], 403)

    def test_rate_limit(self):
        for _ in range(5):
            self.assertEqual(self.req('POST', '/api/contatto', lead())[0], 503)
        self.assertEqual(self.req('POST', '/api/contatto', lead())[0], 429)
        self.assertEqual(self.req('POST', '/api/contatto', lead(), ip='198.51.100.1')[0], 503)

    def test_rate_limiter_window(self):
        rl = S.RateLimiter(2, 10)
        self.assertTrue(rl.allow('a', 0)); self.assertTrue(rl.allow('a', 1)); self.assertFalse(rl.allow('a', 2))
        self.assertTrue(rl.allow('a', 10.5))

    def test_honeypot(self):
        os.environ['RESEND_API_KEY'] = 'k'
        with mock.patch.object(S, 'send_mail') as sm:
            self.assertEqual(self.req('POST', '/api/contatto', lead(website='http://spam')), (200, {'ok': True}))
            sm.assert_not_called()


class TestValidation(unittest.TestCase):
    def ok(self, **over):
        return S.validate_lead(lead(**over))

    def bad(self, field, **over):
        with self.assertRaises(S.Invalid) as cm:
            S.validate_lead(lead(**over))
        self.assertEqual(str(cm.exception), field)

    def test_valid(self):
        v = self.ok()
        self.assertEqual(v['name'], 'Mario Rossi')
        self.assertEqual(v['attribution'], {'gclid': 'abc123', 'utm_source': 'google'})

    def test_rules(self):
        self.bad('name', name='')
        self.bad('name', name='x' * 151)
        self.bad('name', name='a\nBcc: x@y.z')
        self.bad('email', email='non-email')
        self.bad('email', email='a@b')
        self.bad('email', email='a' * 250 + '@ex.com')
        self.bad('company', company='x' * 201)
        self.bad('phone', phone='1' * 41)
        self.bad('phone', phone='chiamami')
        self.bad('need', need='x' * 2001)
        self.bad('message', message='x' * 5001)
        self.bad('message', message='', need='')
        self.bad('privacy', privacy=False)
        self.bad('privacy', privacy='true')
        self.bad('tipo', name=123)
        self.bad('attribution', attribution='x')
        self.assertEqual(self.ok(phone='', company='', need='')['phone'], '')

    def test_not_dict(self):
        with self.assertRaises(S.Invalid):
            S.validate_lead([1])

    def test_email_escaped(self):
        subject, text, body = S.team_email(self.ok(name='<script>x</script>'))
        self.assertNotIn('<script>x', body)
        self.assertIn('&lt;script&gt;', body)
        self.assertIn('--- Provenienza ---', text)
        self.assertIn('gclid', body)
        _, _, vbody = S.visitor_email(self.ok())
        self.assertNotIn('subito', vbody)  # la conferma non ripete il messaggio
        self.assertIn('odyra-mark.png', vbody)
        self.assertNotIn('resend', (body + vbody).lower())


class TestDelivery(Base):
    def test_api_ok(self):
        os.environ['RESEND_API_KEY'] = 'k'
        with mock.patch.object(S, 'send_api') as sa:
            self.assertEqual(self.req('POST', '/api/contatto', lead()), (200, {'ok': True}))
        self.assertEqual(sa.call_count, 2)
        self.assertEqual(sa.call_args_list[0].args[0], 'team@odyrasystemautomation.it')
        self.assertEqual(sa.call_args_list[0].kwargs['reply_to'], 'mario@example.com')
        self.assertEqual(sa.call_args_list[1].args[0], 'mario@example.com')

    def test_api_request_shape(self):
        os.environ['RESEND_API_KEY'] = 'chiave'
        resp = mock.MagicMock(); resp.__enter__.return_value.status = 200
        with mock.patch.object(S.urllib.request, 'urlopen', return_value=resp) as uo:
            S.send_api('a@b.it', 'Oggetto', 'testo', '<p>x</p>', reply_to='c@d.it')
        r = uo.call_args.args[0]
        self.assertEqual(r.full_url, 'https://api.resend.com/emails')
        self.assertEqual(r.get_header('Authorization'), 'Bearer chiave')
        body = json.loads(r.data)
        self.assertEqual(body['from'], 'Odyra <noreply@odyrasystemautomation.it>')
        self.assertEqual(body['reply_to'], 'c@d.it')
        self.assertEqual(uo.call_args.kwargs['timeout'], 10)

    def test_all_fail_502(self):
        os.environ['RESEND_API_KEY'] = 'k'
        with mock.patch.object(S, 'send_api', side_effect=OSError('down')):
            self.assertEqual(self.req('POST', '/api/contatto', lead())[0], 502)

    def test_confirmation_failure_still_ok(self):
        os.environ['RESEND_API_KEY'] = 'k'
        with mock.patch.object(S, 'send_api', side_effect=[None, OSError('x')]):
            self.assertEqual(self.req('POST', '/api/contatto', lead())[0], 200)

    def test_smtp(self):
        FakeSMTP.messages = []
        smtp = socketserver.ThreadingTCPServer(('127.0.0.1', 0), FakeSMTP)
        smtp.daemon_threads = True
        threading.Thread(target=smtp.serve_forever, daemon=True).start()
        try:
            os.environ.update(SMTP_HOST='127.0.0.1', SMTP_PORT=str(smtp.server_address[1]), MAIL_TO='vendite@example.com')
            self.assertEqual(self.req('POST', '/api/contatto', lead()), (200, {'ok': True}))
        finally:
            smtp.shutdown(); smtp.server_close()
        self.assertEqual(len(FakeSMTP.messages), 2)
        rcpt, msg = FakeSMTP.messages[0]
        self.assertEqual(rcpt, ['<vendite@example.com>'])
        self.assertIn('Reply-To: mario@example.com', msg)
        self.assertIn('From: Odyra <noreply@odyrasystemautomation.it>', msg)
        self.assertEqual(FakeSMTP.messages[1][0], ['<mario@example.com>'])

    def test_smtp_refuses_plaintext_login(self):
        FakeSMTP.messages = []
        smtp = socketserver.ThreadingTCPServer(('127.0.0.1', 0), FakeSMTP)
        threading.Thread(target=smtp.serve_forever, daemon=True).start()
        try:
            os.environ.update(SMTP_HOST='127.0.0.1', SMTP_PORT=str(smtp.server_address[1]), SMTP_USER='u', SMTP_PASSWORD='p')
            self.assertEqual(self.req('POST', '/api/contatto', lead())[0], 502)
        finally:
            smtp.shutdown(); smtp.server_close()
        self.assertEqual(FakeSMTP.messages, [])

    def test_smtp_unreachable_502(self):
        s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
        os.environ.update(SMTP_HOST='127.0.0.1', SMTP_PORT=str(port))
        self.assertEqual(self.req('POST', '/api/contatto', lead())[0], 502)

    def test_webhook(self):
        Hook.received, Hook.status = [], 200
        hook = ThreadingHTTPServer(('127.0.0.1', 0), Hook)
        threading.Thread(target=hook.serve_forever, daemon=True).start()
        try:
            os.environ['LEAD_WEBHOOK_URL'] = f'http://127.0.0.1:{hook.server_address[1]}/lead'
            self.assertEqual(self.req('POST', '/api/contatto', lead()), (200, {'ok': True}))
            Hook.status = 500
            self.assertEqual(self.req('POST', '/api/contatto', lead())[0], 502)
            # webhook giù ma e-mail riuscita: 200
            os.environ['RESEND_API_KEY'] = 'k'
            with mock.patch.object(S, 'send_api'):
                self.assertEqual(self.req('POST', '/api/contatto', lead())[0], 200)
        finally:
            hook.shutdown(); hook.server_close()
        self.assertEqual(Hook.received[0]['source'], 'odyra_website_form')
        self.assertEqual(Hook.received[0]['email'], 'mario@example.com')
        self.assertEqual(Hook.received[0]['attribution'], {'gclid': 'abc123', 'utm_source': 'google'})


class TestVoice(Base):
    def conf(self):
        os.environ.update(LIVEKIT_URL='wss://demo.example.cloud', LIVEKIT_API_KEY='APIkey', LIVEKIT_API_SECRET='segreto-lungo')

    def test_503(self):
        self.assertEqual(self.req('POST', '/api/voce/token', {'lang': 'it'}), (503, {'error': 'non_configurato'}))

    def test_token(self):
        self.conf()
        st, b = self.req('POST', '/api/voce/token', {'lang': 'es'})
        self.assertEqual(st, 200)
        self.assertEqual(b['url'], 'wss://demo.example.cloud')
        self.assertEqual(b['lang'], 'es')
        h, p, s = b['token'].split('.')
        self.assertEqual(json.loads(b64d(h)), {'alg': 'HS256', 'typ': 'JWT'})
        sig = hmac.new(b'segreto-lungo', f'{h}.{p}'.encode(), hashlib.sha256).digest()
        self.assertTrue(hmac.compare_digest(sig, b64d(s)))
        c = json.loads(b64d(p))
        self.assertEqual(c['iss'], 'APIkey')
        self.assertRegex(c['sub'], r'^visitor-[0-9a-f]{8}$')
        self.assertEqual(c['exp'] - c['iat'], 600)
        self.assertLessEqual(abs(c['iat'] - time.time()), 5)
        self.assertEqual(c['name'], 'Visitatore')
        self.assertRegex(c['video']['room'], r'^odyra-web-[0-9a-f-]{36}$')
        self.assertEqual(c['video']['room'], b['room'])
        self.assertEqual({k: v for k, v in c['video'].items() if k != 'room'},
                         {'roomJoin': True, 'canPublish': True, 'canPublishSources': ['microphone'], 'canSubscribe': True,
                          'canPublishData': False, 'canUpdateOwnMetadata': False})
        # nessun permesso di amministrazione, creazione, elenco, registrazione, SIP; niente metadati del partecipante
        for k in ('roomAdmin', 'roomCreate', 'roomList', 'roomRecord', 'ingressAdmin', 'hidden', 'destinationRoom'):
            self.assertNotIn(k, c['video'])
        for k in ('sip', 'metadata', 'attributes'):
            self.assertNotIn(k, c)
        self.assertEqual(c['roomConfig']['maxParticipants'], 3)
        self.assertLessEqual(c['roomConfig']['emptyTimeout'], 60)
        self.assertEqual(c['roomConfig']['agents'][0]['agentName'], 'odyra_web')
        self.assertEqual(json.loads(c['roomConfig']['agents'][0]['metadata']), {'lang': 'es'})

    def test_lang_default_and_agent_name(self):
        self.conf(); os.environ['VOICE_AGENT_NAME'] = 'altro'
        b = self.req('POST', '/api/voce/token', {'lang': 'xx'})[1]
        c = json.loads(b64d(b['token'].split('.')[1]))
        self.assertEqual(b['lang'], 'it')
        self.assertEqual(c['roomConfig']['agents'][0]['agentName'], 'altro')
        self.assertEqual(self.req('POST', '/api/voce/token', {})[1]['lang'], 'it')

    def test_origin_and_rate(self):
        self.conf()
        self.assertEqual(self.req('POST', '/api/voce/token', {}, headers={'Origin': 'https://evil.example'})[0], 403)
        for _ in range(5):
            self.assertEqual(self.req('POST', '/api/voce/token', {})[0], 200)
        self.assertEqual(self.req('POST', '/api/voce/token', {})[0], 429)



class TestSecurity(Base):
    """Scenari d'attacco: IP falsificati, limiti, corpi anomali, metodi, errori, intestazioni."""

    def raw(self, data, timeout=5):
        """Manda byte grezzi e restituisce la risposta grezza (o b'' se il server chiude)."""
        s = socket.create_connection(('127.0.0.1', self.port), timeout=timeout)
        try:
            s.sendall(data)
            out = b''
            while True:
                chunk = s.recv(65536)
                if not chunk:
                    break
                out += chunk
            return out
        finally:
            s.close()

    def test_rate_limit_ignores_x_forwarded_for(self):
        # il client cambia X-Forwarded-For a ogni richiesta, ma X-Real-IP (scritto da nginx) resta lo stesso
        for i in range(5):
            st, _ = self.req('POST', '/api/contatto', lead(), headers={'X-Forwarded-For': f'10.0.0.{i}'})
            self.assertEqual(st, 503)
        self.assertEqual(self.req('POST', '/api/contatto', lead(), headers={'X-Forwarded-For': '10.9.9.9'})[0], 429)

    def test_ip_key(self):
        self.assertEqual(S.ip_key('203.0.113.7', '127.0.0.1'), '203.0.113.7')
        # IPv6: stessa /64 = stessa chiave
        self.assertEqual(S.ip_key('2001:db8:1:2::1', '127.0.0.1'), S.ip_key('2001:db8:1:2:ffff::9', '127.0.0.1'))
        self.assertNotEqual(S.ip_key('2001:db8:1:2::1', '127.0.0.1'), S.ip_key('2001:db8:1:3::1', '127.0.0.1'))
        self.assertEqual(S.ip_key('::ffff:198.51.100.4', '127.0.0.1'), '198.51.100.4')
        # valori non validi o enormi: indirizzo della connessione (chiavi sempre corte e ben formate)
        self.assertEqual(S.ip_key('x' * 5000, '127.0.0.1'), '127.0.0.1')
        self.assertEqual(S.ip_key('1.2.3.4, 5.6.7.8', '127.0.0.1'), '127.0.0.1')
        self.assertEqual(S.ip_key(None, '127.0.0.1'), '127.0.0.1')

    def test_ipv6_rotation_limited(self):
        for i in range(5):
            self.assertEqual(self.req('POST', '/api/contatto', lead(), ip=f'2001:db8:aa:bb::{i + 1}')[0], 503)
        self.assertEqual(self.req('POST', '/api/contatto', lead(), ip='2001:db8:aa:bb::99')[0], 429)

    def test_rate_limiter_memory_bounded(self):
        rl = S.RateLimiter(5, 600, max_keys=100)
        for i in range(10000):
            rl.allow(f'k{i}', now=1.0)
        self.assertLessEqual(len(rl.hits), 100)
        # le chiavi scadute si liberano da sole
        rl.allow('nuova', now=1000.0)
        self.assertEqual(list(rl.hits), ['nuova'])

    def test_rate_limiter_is_fast_with_many_keys(self):
        rl = S.RateLimiter(5, 600, max_keys=20000)
        t = time.perf_counter()
        for i in range(60000):
            rl.allow(f'k{i}', now=1.0 + i / 1e6)
        self.assertLess(time.perf_counter() - t, 5)
        self.assertLessEqual(len(rl.hits), 20000)

    def test_global_cap_voice(self):
        os.environ.update(LIVEKIT_URL='wss://demo.example.cloud', LIVEKIT_API_KEY='k', LIVEKIT_API_SECRET='s',
                          VOICE_MAX_PER_HOUR='3')
        for i in range(3):
            self.assertEqual(self.req('POST', '/api/voce/token', {}, ip=f'198.51.100.{i}')[0], 200)
        self.assertEqual(self.req('POST', '/api/voce/token', {}, ip='198.51.100.50')[0], 429)

    def test_voice_daily_cap_per_ip(self):
        os.environ.update(LIVEKIT_URL='wss://x.example', LIVEKIT_API_KEY='k', LIVEKIT_API_SECRET='s')
        S.LIMIT_VOICE.limit = 1000
        try:
            codes = [self.req('POST', '/api/voce/token', {})[0] for _ in range(21)]
        finally:
            S.LIMIT_VOICE.limit = 5
        self.assertEqual(codes[:20], [200] * 20)
        self.assertEqual(codes[20], 429)

    def test_voice_rooms_unique_and_metadata_fixed(self):
        os.environ.update(LIVEKIT_URL='wss://x.example', LIVEKIT_API_KEY='k', LIVEKIT_API_SECRET='s')
        a = self.req('POST', '/api/voce/token', {'lang': 'it', 'metadata': '{"admin":true}', 'room': 'altra'})[1]
        b = self.req('POST', '/api/voce/token', {'lang': 'it"}'})[1]
        self.assertNotEqual(a['room'], b['room'])
        for t in (a, b):
            c = json.loads(b64d(t['token'].split('.')[1]))
            self.assertEqual(json.loads(c['roomConfig']['agents'][0]['metadata']), {'lang': 'it'})
            self.assertTrue(c['video']['room'].startswith('odyra-web-'))

    def test_contact_global_cap(self):
        os.environ['CONTACT_MAX_PER_HOUR'] = '2'
        self.assertEqual(self.req('POST', '/api/contatto', lead(), ip='192.0.2.1')[0], 503)
        self.assertEqual(self.req('POST', '/api/contatto', lead(), ip='192.0.2.2')[0], 503)
        self.assertEqual(self.req('POST', '/api/contatto', lead(), ip='192.0.2.3')[0], 429)

    def test_confirmation_limited_per_recipient(self):
        os.environ['RESEND_API_KEY'] = 'k'
        with mock.patch.object(S, 'send_api') as sa:
            for i in range(4):
                self.assertEqual(self.req('POST', '/api/contatto', lead(email='Vittima@example.com'), ip=f'192.0.2.{i}')[0], 200)
        to = [c.args[0] for c in sa.call_args_list]
        self.assertEqual(to.count('team@odyrasystemautomation.it'), 4)
        self.assertEqual(to.count('Vittima@example.com'), 2)

    def test_confirmation_does_not_relay_content(self):
        v = S.validate_lead(lead(name='Visita http://spam.example ora', message='Compra qui: http://spam.example'))
        subject, text, body = S.visitor_email(v)
        self.assertNotIn('spam.example', text + body + subject)
        self.assertTrue(text.startswith('Ciao Visita,'))
        v = S.validate_lead(lead(name='http://spam.example'))
        self.assertTrue(S.visitor_email(v)[1].startswith('Ciao,'))
        self.assertEqual(S.greeting_name("D'Angelo Rossi"), "D'Angelo")
        self.assertEqual(S.greeting_name('José'), 'José')
        self.assertEqual(S.greeting_name('<b>x</b>'), '')

    def test_header_injection_unicode(self):
        for evil in ('Mario\x85Bcc: x@y.z', 'Mario\rBcc: x@y.z', 'Mario\tRossi'):
            with self.assertRaises(S.Invalid, msg=repr(evil)):
                S.validate_lead(lead(name=evil))
        # separatori di riga Unicode, invisibili e controlli bidi tolti: nessuna interruzione di riga possibile
        self.assertEqual(S.validate_lead(lead(name='Mario\u2028Bcc: x@y.z'))['name'], 'MarioBcc: x@y.z')
        v = S.validate_lead(lead(name='Ma\u202erio\u200b', company='Ro\x00ssi\x9b'))
        self.assertEqual((v['name'], v['company']), ('Mario', 'Rossi'))
        for evil in ('a@b.it\nBcc: x@y.z', 'a@b.it, c@d.it', '"x"@b.it', 'Nome <a@b.it>', '.a@b.it', 'a..b@c.it',
                     'a' * 65 + '@b.it'):
            with self.assertRaises(S.Invalid, msg=repr(evil)):
                S.validate_lead(lead(email=evil))

    def test_smtp_headers_not_injectable(self):
        v = S.validate_lead(lead(name='Mario Rossi', company='ACME'))
        subject, text, body = S.team_email(v)
        self.assertNotIn('\n', subject)
        self.assertNotIn('\r', subject)

    def test_html_injection_everywhere(self):
        v = S.validate_lead(lead(company='"><img src=x onerror=alert(1)>', need='<a href="http://x">y</a>',
                                 attribution={'utm_source': '<script>alert(1)</script>', 'referrer': '"><svg/onload=1>'}))
        _, _, body = S.team_email(v)
        for bad in ('<img src=x', '<a href="http://x"', '<script>alert', '<svg/onload'):
            self.assertNotIn(bad, body)

    def test_deep_json_is_400_not_crash(self):
        st, b = self.req('POST', '/api/contatto', raw=b'[' * 8000 + b']' * 8000)
        self.assertEqual(st, 400)
        body = json.dumps(lead()).encode()
        with mock.patch.object(S.json, 'loads', side_effect=RecursionError):
            r = self.raw(b'POST /api/contatto HTTP/1.1\r\nHost: x\r\nContent-Type: application/json\r\nOrigin: ' + ORIGIN.encode() +
                         b'\r\nConnection: close\r\nContent-Length: ' + str(len(body)).encode() + b'\r\n\r\n' + body)
        self.assertIn(b' 400 ', r.split(b'\r\n')[0])
        self.assertTrue(r.endswith(b'{"error": "json"}'), r[-60:])
        self.assertEqual(self.req('GET', '/api/salute')[0], 200)  # server ancora vivo

    def test_content_length_missing_or_bad(self):
        r = self.raw(b'POST /api/contatto HTTP/1.1\r\nHost: x\r\nContent-Type: application/json\r\nOrigin: ' +
                     ORIGIN.encode() + b'\r\nConnection: close\r\n\r\n{}')
        self.assertIn(b' 411 ', r.split(b'\r\n')[0])
        r = self.raw(b'POST /api/contatto HTTP/1.1\r\nHost: x\r\nContent-Type: application/json\r\nContent-Length: abc\r\n'
                     b'Connection: close\r\n\r\n{}')
        self.assertIn(b' 411 ', r.split(b'\r\n')[0])
        r = self.raw(b'POST /api/contatto HTTP/1.1\r\nHost: x\r\nContent-Type: application/json\r\nContent-Length: 99999999999\r\n'
                     b'Connection: close\r\n\r\n{}')
        self.assertIn(b' 413 ', r.split(b'\r\n')[0])
        r = self.raw(b'POST /api/contatto HTTP/1.1\r\nHost: x\r\nContent-Type: application/json\r\nTransfer-Encoding: chunked\r\n'
                     b'Connection: close\r\n\r\n2\r\n{}\r\n0\r\n\r\n')
        self.assertIn(b' 411 ', r.split(b'\r\n')[0])

    def test_slow_client_times_out(self):
        # dichiara 100 byte e ne manda 2: il server non resta appeso per sempre
        with mock.patch.object(S.Handler, 'timeout', 1):
            t = time.monotonic()
            r = self.raw(b'POST /api/contatto HTTP/1.1\r\nHost: x\r\nContent-Type: application/json\r\nContent-Length: 100\r\n'
                         b'Origin: ' + ORIGIN.encode() + b'\r\n\r\n{}', timeout=10)
            self.assertLess(time.monotonic() - t, 5)
        self.assertTrue(r == b'' or b' 408 ' in r.split(b'\r\n')[0], r[:80])
        # e una connessione che non manda nemmeno la riga di richiesta viene chiusa
        with mock.patch.object(S.Handler, 'timeout', 1):
            s = socket.create_connection(('127.0.0.1', self.port), timeout=10)
            t = time.monotonic()
            self.assertEqual(s.recv(10), b'')
            self.assertLess(time.monotonic() - t, 5)
            s.close()

    def test_methods(self):
        for m in ('PUT', 'DELETE', 'PATCH', 'OPTIONS', 'TRACE'):
            st, b = self.req(m, '/api/contatto', {})
            self.assertEqual((st, b), (405, {'error': 'metodo'}), m)
        st, b = self.req('GET', '/api/contatto')
        self.assertEqual(st, 405)
        r = self.raw(b'FOO /api/contatto HTTP/1.1\r\nHost: x\r\nConnection: close\r\n\r\n')
        self.assertIn(b'application/json', r)
        self.assertNotIn(b'<html', r.lower())

    def test_path_variants_not_routed(self):
        os.environ.update(LIVEKIT_URL='wss://x.example', LIVEKIT_API_KEY='k', LIVEKIT_API_SECRET='s')
        for path in ('/api/voce/token/', '/api/voce/../voce/token', '/API/voce/token', '/api/voce/token%00'):
            self.assertEqual(self.req('POST', path, {})[0], 404, path)

    def test_no_stack_in_responses(self):
        with mock.patch.object(S, 'validate_lead', side_effect=KeyError('segreto')):
            st, b = self.req('POST', '/api/contatto', lead())
        self.assertEqual((st, b), (500, {'error': 'errore_interno'}))
        with mock.patch.object(S, 'voice_token', side_effect=ValueError('LIVEKIT_API_SECRET=xyz')):
            os.environ.update(LIVEKIT_URL='wss://x.example', LIVEKIT_API_KEY='k', LIVEKIT_API_SECRET='s')
            st, b = self.req('POST', '/api/voce/token', {})
        self.assertEqual((st, b), (500, {'error': 'errore_interno'}))

    def test_api_headers(self):
        c = http.client.HTTPConnection('127.0.0.1', self.port, timeout=5)
        c.request('GET', '/api/salute')
        r = c.getresponse(); r.read(); c.close()
        self.assertEqual(r.getheader('Cache-Control'), 'no-store')
        self.assertEqual(r.getheader('X-Content-Type-Options'), 'nosniff')
        self.assertTrue(r.getheader('Content-Type').startswith('application/json'))
        self.assertEqual(r.getheader('Server'), 'odyra-api')  # nessuna versione di Python

    def test_origin_same_host_and_referer(self):
        # stessa origine dell'Host (sito servito da un dominio non in elenco)
        st, _ = self.req('POST', '/api/contatto', lead(), headers={'Origin': 'https://anteprima.example', 'Host': 'anteprima.example'})
        self.assertEqual(st, 503)
        # stesso host ma http (non localhost): rifiutato
        st, _ = self.req('POST', '/api/contatto', lead(), headers={'Origin': 'http://anteprima.example', 'Host': 'anteprima.example'})
        self.assertEqual(st, 403)
        # Referer di un altro sito, Origin "null" (iframe sandbox, file://)
        self.assertEqual(self.req('POST', '/api/contatto', lead(), headers={'Origin': 'null', 'Referer': 'https://evil.example/x'})[0], 403)
        self.assertEqual(self.req('POST', '/api/contatto', lead(), headers={'Origin': 'null'})[0], 403)
        # host che contiene quello ammesso
        for o in ('https://odyrasystemautomation.it.evil.example', 'https://evilodyrasystemautomation.it',
                  'https://odyrasystemautomation.it@evil.example'):
            self.assertEqual(self.req('POST', '/api/contatto', lead(), headers={'Origin': o})[0], 403, o)

    def test_webhook_scheme(self):
        os.environ['LEAD_WEBHOOK_URL'] = 'file:///etc/passwd'
        self.assertEqual(self.req('POST', '/api/contatto', lead())[0], 502)


if __name__ == '__main__':
    unittest.main()
