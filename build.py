#!/usr/bin/env python3
"""Genera il sito Odyra (italiano in radice, spagnolo in /es/). Uso: python3 build.py"""
import os, html, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://odyrasystemautomation.it'
EMAIL = 'team@odyrasystemautomation.it'
L = 'it'

def t(it, es):
    return it if L == 'it' else es

def e(s):
    return html.escape(s, quote=True)

ICON = {
    'phone': '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
    'chat': '<path d="M21 12a8 8 0 0 1-11.5 7.2L4 20l1-4.5A8 8 0 1 1 21 12z"/>',
    'cal': '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M8 3v4M16 3v4M3 10h18"/>',
    'bell': '<path d="M6 9a6 6 0 0 1 12 0c0 6 2 7 2 7H4s2-1 2-7zM10 20a2 2 0 0 0 4 0"/>',
    'book': '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2zM4 19V5"/>',
    'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    'chart': '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    'bolt': '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    'layers': '<path d="M12 3l9 5-9 5-9-5zM3 13l9 5 9-5M3 17.5l9 5 9-5"/>',
    'plug': '<path d="M9 2v6M15 2v6M6 8h12v4a6 6 0 0 1-12 0zM12 18v4"/>',
    'mic': '<rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>',
    'shield': '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    'server': '<rect x="3" y="4" width="18" height="7" rx="2"/><rect x="3" y="13" width="18" height="7" rx="2"/><path d="M7 7.5h.01M7 16.5h.01"/>',
    'brain': '<path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 6 1V4a3 3 0 0 0-3 0zM15 4a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3 3 0 0 1-2 5 3 3 0 0 1-6 1"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M3 8l9 6 9-6"/>',
    'box': '<path d="M21 8l-9-5-9 5v8l9 5 9-5zM3 8l9 5 9-5M12 13v8"/>',
    'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    'handshake': '<path d="M3 11l4-4 4 2 4-2 6 5-5 5-3-2-3 3-4-3z"/>',
    'cog': '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/>',
}

def ic(n):
    return f'<span class="ico"><svg viewBox="0 0 24 24" aria-hidden="true">{ICON[n]}</svg></span>'

PAGES = [
    # slug, file
    ('home', 'index.html'),
    ('gruppo', 'gruppo.html'),
    ('voce', 'agenti-ai-vocali-whatsapp.html'),
    ('commerciale', 'agente-commerciale-ai.html'),
    ('hako', 'hako.html'),
    ('software-house', 'software-house.html'),
    ('enterprise', 'enterprise.html'),
    ('casi', 'casi-studio.html'),
    ('tecnologia', 'tecnologia.html'),
    ('contatti', 'contatti.html'),
]
FILE = dict(PAGES)

def url(slug, lang=None):
    lang = lang or L
    f = FILE[slug]
    base = '/' if lang == 'it' else '/es/'
    return base if f == 'index.html' else base + f

def layout(slug, title, desc, body, extra_head='', hero_c=None):
    other = 'es' if L == 'it' else 'it'
    nav_active = lambda s: ' aria-current="page"' if s == slug else ''
    prods = [
        ('voce', 'var(--c-voce)', t('Agenti AI vocali e WhatsApp', 'Agentes IA de voz y WhatsApp'), t('La receptionist AI che prenota nel gestionale', 'La recepcionista IA que reserva en tu software')),
        ('commerciale', 'var(--c-comm)', t('Agente commerciale AI', 'Agente comercial IA'), t('Ogni lead richiamato in meno di un minuto', 'Cada lead llamado en menos de un minuto')),
        ('hako', 'var(--c-hako)', 'HAKO', t('Pacchi in portineria, condomini avvisati', 'Paquetes en conserjería, vecinos avisados')),
    ]
    dd = ''.join(f'<a href="{url(s)}"><i class="dot" style="background:{c}"></i><span><b>{e(n)}</b><small>{e(d)}</small></span></a>' for s, c, n, d in prods)
    sdd = ''.join(f'<a href="{url(s)}"><i class="dot" style="background:var(--blue)"></i><span><b>{e(n)}</b><small>{e(d)}</small></span></a>' for s, n, d in [
        ('software-house', t('Per le software house', 'Para software houses'), t('AI white-label con il tuo marchio', 'IA white-label con tu marca')),
        ('enterprise', 'Enterprise', t('Progetti su misura per grandi volumi', 'Proyectos a medida para grandes volúmenes')),
    ])
    nav = f'''<nav class="nav" id="nav" aria-label="{t('Principale','Principal')}">
      <div class="dd"><button aria-expanded="false" aria-haspopup="true">{t('Prodotti','Productos')} <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="2"/></svg></button><div class="dd-menu">{dd}</div></div>
      <div class="dd"><button aria-expanded="false" aria-haspopup="true">{t('Servizi','Servicios')} <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="2"/></svg></button><div class="dd-menu">{sdd}</div></div>
      <a href="{url('casi')}"{nav_active('casi')}>{t('Casi studio','Casos de éxito')}</a>
      <a href="{url('tecnologia')}"{nav_active('tecnologia')}>{t('Tecnologia','Tecnología')}</a>
      <a href="{url('gruppo')}"{nav_active('gruppo')}>{t('Il gruppo','El grupo')}</a>
      <div class="lang" role="group" aria-label="Lingua"><a href="{url(slug,'it')}" hreflang="it"{' aria-current="true"' if L=='it' else ''}>IT</a><a href="{url(slug,'es')}" hreflang="es"{' aria-current="true"' if L=='es' else ''}>ES</a></div>
      <a class="btn btn-p btn-sm" href="{url('contatti')}">{t('Parla con noi','Habla con nosotros')}</a>
    </nav>'''
    path = url(slug)
    alt = ''.join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{url(slug, l)}">' for l in ('it', 'es')) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{url(slug, "it")}">'
    style = f' style="--hero-c:{hero_c}"' if hero_c else ''
    return f'''<!doctype html>
<html lang="{L}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}{path}">
{alt}
<meta property="og:type" content="website"><meta property="og:site_name" content="Odyra System">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE}{path}"><meta property="og:image" content="{SITE}/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#3B82F6">
<link rel="icon" href="/assets/icon.svg" type="image/svg+xml">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Unbounded:wght@500;600;700&display=swap">
<link rel="stylesheet" href="/styles.css?v=1">
{extra_head}
</head>
<body{style}>
<a class="skip" href="#main">{t('Vai al contenuto','Ir al contenido')}</a>
<header class="hdr" id="top"><div class="wrap">
  <a class="brand" href="{url('home')}" aria-label="Odyra System"><img src="/assets/logos/odyra.png" alt="Odyra System" width="150" height="40"></a>
  {nav}
  <button class="burger" id="burger" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
</div></header>
<main id="main">
{body}
</main>
{footer()}
<script src="/script.js?v=1" defer></script>
</body>
</html>
'''

def footer():
    return f'''<footer class="ftr"><div class="wrap">
  <div class="top">
    <div>
      <div class="pill"><img src="/assets/logos/odyra.png" alt="Odyra System"></div>
      <p>{t('Software AI proprietari, progettati a Milano. Agenti che rispondono, vendono e organizzano dentro i software che usi già.','Software de IA propio, diseñado en Milán. Agentes que responden, venden y organizan dentro del software que ya usas.')}</p>
      <div class="partners" aria-label="{t('Canali e infrastruttura','Canales e infraestructura')}">
        <img src="/assets/logos/whatsapp.svg" alt="WhatsApp"><img src="/assets/logos/meta.svg" alt="Meta"><img src="/assets/logos/vonage.svg" alt="Vonage">
      </div>
    </div>
    <div><h4>{t('Prodotti','Productos')}</h4><ul>
      <li><a href="{url('voce')}">{t('Agenti AI vocali e WhatsApp','Agentes IA de voz y WhatsApp')}</a></li>
      <li><a href="{url('commerciale')}">{t('Agente commerciale AI','Agente comercial IA')}</a></li>
      <li><a href="{url('hako')}">HAKO</a></li></ul></div>
    <div><h4>{t('Azienda','Empresa')}</h4><ul>
      <li><a href="{url('gruppo')}">{t('Il gruppo','El grupo')}</a></li>
      <li><a href="{url('software-house')}">{t('Per le software house','Para software houses')}</a></li>
      <li><a href="{url('enterprise')}">Enterprise</a></li>
      <li><a href="{url('casi')}">{t('Casi studio','Casos de éxito')}</a></li>
      <li><a href="{url('tecnologia')}">{t('Tecnologia e sicurezza','Tecnología y seguridad')}</a></li></ul></div>
    <div><h4>{t('Contatti','Contacto')}</h4><ul>
      <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
      <li>Verypos S.r.l.<br>Viale Papiniano 8<br>20123 Milano</li>
      <li><a href="{url('contatti')}">{t('Scrivici dal modulo','Escríbenos desde el formulario')}</a></li></ul></div>
  </div>
  <div class="bot"><span>© {datetime.date.today().year} Odyra System · Verypos S.r.l. · P.IVA 11630390968 · REA MI-2615892</span>
  <span><a href="{'/privacy.html' if L=='it' else '/es/privacy.html'}">Privacy</a> · {t('WhatsApp e Meta sono marchi dei rispettivi proprietari.','WhatsApp y Meta son marcas de sus respectivos propietarios.')}</span></div>
</div></footer>'''

def cta(title=None, sub=None, interesse=''):
    title = title or t('Parliamo del tuo caso.', 'Hablemos de tu caso.')
    sub = sub or t('Raccontaci come lavori oggi. Ti mostriamo dove l\'AI recupera chiamate, lead e tempo.', 'Cuéntanos cómo trabajas hoy. Te mostramos dónde la IA recupera llamadas, leads y tiempo.')
    q = f'?interesse={interesse}' if interesse else ''
    return f'''<section style="padding-top:0"><div class="wrap"><div class="cta-band rv">
  <div><h2>{title}</h2><p>{sub}</p></div>
  <a class="btn btn-w" href="{url('contatti')}{q}">{t('Richiedi una demo','Solicita una demo')} →</a>
</div></div></section>'''

def call_demo():
    return f'''<div class="device rv" aria-label="{t('Esempio di chiamata gestita dall\'agente AI','Ejemplo de llamada gestionada por el agente IA')}">
  <div class="dv-top"><div class="dv-av">AI</div><div><b>{t('Salone Aurora','Salón Aurora')}</b><small>{t('Chiamata in arrivo · 21:47','Llamada entrante · 21:47')}</small></div><span class="live">{t('IN LINEA','EN LÍNEA')}</span></div>
  <div class="wave" aria-hidden="true">{''.join('<i style="animation-delay:%.2fs"></i>' % (i*0.07) for i in range(26))}</div>
  <div class="msgs">
    <div class="msg ai">{t('Buonasera, Salone Aurora. Come posso aiutarla?','Buenas noches, Salón Aurora. ¿En qué puedo ayudarle?')}</div>
    <div class="msg cl">{t('Vorrei un taglio e piega venerdì pomeriggio.','Quisiera un corte y peinado el viernes por la tarde.')}</div>
    <div class="msg ai">{t('Venerdì alle 15:30 con Giulia è libero. Prenoto?','El viernes a las 15:30 con Giulia está libre. ¿Reservo?')}</div>
    <div class="msg cl">{t('Sì, grazie.','Sí, gracias.')}</div>
  </div>
  <div class="confirm"><img src="/assets/logos/whatsapp.svg" alt="WhatsApp"><div><b>{t('Prenotazione nel gestionale','Reserva en el software')}</b>{t('Ven 15:30 · Taglio e piega · conferma inviata','Vie 15:30 · Corte y peinado · confirmación enviada')}</div></div>
  <p class="tag-ex">{t('Esempio illustrativo','Ejemplo ilustrativo')}</p>
</div>'''

def goagent_wm(sm=False):
    return f'<span class="wm{" sm" if sm else ""}"><span class="g">G</span>GoAgent</span>'

def video_slot(name):
    return f'<div class="media rv" hidden data-video="/assets/video/{name}.mp4"><video controls playsinline preload="metadata" poster="/assets/video/{name}.jpg"></video></div>'

def audio_slot():
    return f'''<section id="audio-demo" class="alt" hidden><div class="wrap">
  <div class="sec-h"><span class="eyebrow">{t('Ascolta','Escucha')}</span><h2>{t('Chiamate reali dell\'agente.','Llamadas reales del agente.')}</h2><p class="lead">{t('Registrazioni autentiche, nessuna simulazione.','Grabaciones auténticas, sin simulaciones.')}</p></div>
  <div class="audio-list"></div></div></section>'''

# ───────────────────────── HOME ─────────────────────────
def page_home():
    nums = [
        ('24/7', t('Sempre attivo, giorno e notte, festivi inclusi', 'Siempre activo, de día y de noche, festivos incluidos'), None),
        ('<60<em>s</em>', t('Ogni nuovo lead richiamato in meno di un minuto', 'Cada nuevo lead llamado en menos de un minuto'), None),
        ('<1<em>s</em>', t('Conversazioni vocali in tempo reale, senza attese', 'Conversaciones de voz en tiempo real, sin esperas'), None),
        ('262', t('chiamate gestite da GoAgent in 15 giorni, nel primo salone in produzione', 'llamadas gestionadas por GoAgent en 15 días, en el primer salón en producción'), 262),
        ('~1.500', t('saloni nella rete GoWeb a cui BOSS offre GoAgent', 'salones en la red GoWeb a la que BOSS ofrece GoAgent'), None),
        ('10→1.000', t('chiamate: la capacità cresce senza aggiungere personale', 'llamadas: la capacidad crece sin añadir personal'), None),
    ]
    nh = ''.join(f'<div class="rv"><b{f" data-count={c}" if c else ""}>{n}</b><span>{d}</span></div>' for n, d, c in nums)
    claims = [t('Non perdere più una chiamata.', 'No pierdas ni una llamada más.'), t('Il tuo gestionale, ora risponde.', 'Tu software, ahora responde.'), t('Da ore a secondi.', 'De horas a segundos.'), t('Dieci chiamate o mille, stesso team.', 'Diez llamadas o mil, el mismo equipo.'), t('L\'AI che lavora dentro il software che usi già.', 'La IA que trabaja dentro del software que ya usas.'), t('Software proprietari. Risultati misurabili.', 'Software propio. Resultados medibles.')]
    mq = ''.join(f'<span>{c}</span>' for c in claims) * 2
    body = f'''
<section class="hero"><div class="wrap">
  <div>
    <span class="eyebrow">{t('Gruppo tecnologico · Milano','Grupo tecnológico · Milán')}</span>
    <h1>{t('L\'AI che risponde, vende e organizza <span class="grad">al posto tuo.</span>','La IA que responde, vende y organiza <span class="grad">por ti.</span>')}</h1>
    <p class="lead">{t('Software AI proprietari che lavorano dentro le aziende, 24 ore su 24: agenti vocali, agenti su WhatsApp e prodotti verticali, integrati nei gestionali che usi già.','Software de IA propio que trabaja dentro de las empresas, 24 horas al día: agentes de voz, agentes en WhatsApp y productos verticales, integrados en el software que ya usas.')}</p>
    <div class="cta"><a class="btn btn-p" href="#prodotti">{t('Scopri i prodotti','Descubre los productos')}</a><a class="btn btn-o" href="{url('contatti')}">{t('Richiedi una demo','Solicita una demo')}</a></div>
    <div class="proof"><div><b>24/7</b><span>{t('sempre presente','siempre presente')}</span></div><div><b>&lt;60 s</b><span>{t('dal lead alla chiamata','del lead a la llamada')}</span></div><div><b>{t('2 canali','2 canales')}</b><span>{t('voce e WhatsApp','voz y WhatsApp')}</span></div></div>
  </div>
  {call_demo()}
</div></section>

<div class="strip"><div class="wrap"><small>{t('In produzione con','En producción con')}</small>
  <div class="logos">
    <span class="lg"><img class="boss-logo" src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers"><span>BOSS · GoWeb</span></span>
    <span class="lg"><span class="wordmark">Global Trading<small>Gruppo Colzani · Sportit.com</small></span></span>
    <span class="lg"><img src="/assets/logos/hako.png" alt="HAKO" style="height:32px"></span>
  </div></div></div>

<section id="prodotti"><div class="wrap">
  <div class="sec-h"><span class="eyebrow">{t('Il portafoglio','La cartera')}</span><h2>{t('Un gruppo, tanti prodotti, una sola piattaforma.','Un grupo, varios productos, una sola plataforma.')}</h2><p class="lead">{t('Ogni prodotto ha la propria identità e il proprio mercato. Tutti condividono la stessa infrastruttura proprietaria: ogni nuovo prodotto nasce più veloce e più solido del precedente.','Cada producto tiene su propia identidad y su propio mercado. Todos comparten la misma infraestructura propia: cada nuevo producto nace más rápido y más sólido que el anterior.')}</p></div>
  <div class="grid g3">
    <a class="card prod rv" style="--c:var(--c-voce)" href="{url('voce')}"><div class="bar"></div><div class="top">{goagent_wm()}<p style="margin-top:12px"><span class="badge">{t('Agenti AI vocali e WhatsApp','Agentes IA de voz y WhatsApp')}</span></p></div>
      <div class="bd"><p>{t('La receptionist AI risponde a ogni chiamata e messaggio WhatsApp, giorno e notte, e prenota direttamente nel gestionale. Nasce per i saloni con GoAgent, in partnership con BOSS.','La recepcionista IA responde a cada llamada y mensaje de WhatsApp, de día y de noche, y reserva directamente en el software. Nace para los salones con GoAgent, en alianza con BOSS.')}</p><span class="more">{t('Scopri il prodotto','Descubre el producto')}</span></div></a>
    <a class="card prod rv" style="--c:var(--c-comm)" href="{url('commerciale')}"><div class="bar"></div><div class="top"><span class="wm"><span class="g" style="background:var(--c-comm);color:#fff;box-shadow:0 8px 18px -8px rgba(124,92,252,.9)">↗</span>{t('Agente commerciale','Agente comercial')}</span><p style="margin-top:12px"><span class="badge">{t('Speed-to-lead','Speed-to-lead')}</span></p></div>
      <div class="bd"><p>{t('Richiama ogni nuovo lead in meno di un minuto, lo qualifica al telefono in italiano e fissa l\'appuntamento nel calendario del team vendite.','Llama a cada nuevo lead en menos de un minuto, lo califica por teléfono y fija la cita en el calendario del equipo de ventas.')}</p><span class="more">{t('Scopri il prodotto','Descubre el producto')}</span></div></a>
    <a class="card prod rv" style="--c:var(--c-hako)" href="{url('hako')}"><div class="bar"></div><div class="top"><img src="/assets/logos/hako.png" alt="HAKO"><span class="badge">{t('Condomini e portinerie','Comunidades y conserjerías')}</span></div>
      <div class="bd"><p>{t('Il programma della portineria che sostituisce il quaderno dei pacchi: foto, avviso su WhatsApp, SMS o e-mail nella lingua del condomino, ritiro con codice.','El programa de la conserjería que sustituye al cuaderno de paquetes: foto, aviso por WhatsApp, SMS o e-mail en el idioma del vecino, recogida con código.')}</p><span class="more">{t('Scopri il prodotto','Descubre el producto')}</span></div></a>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="sec-h center"><span class="eyebrow">{t('Numeri','Números')}</span><h2>{t('Risultati misurabili, già in produzione.','Resultados medibles, ya en producción.')}</h2></div>
  <div class="nums">{nh}</div>
</div></section>

<section><div class="wrap grid g2" style="align-items:center;gap:56px">
  <div class="rv"><span class="eyebrow">Manifesto</span><h2>{t('Le aziende non hanno bisogno di un altro chatbot.','Las empresas no necesitan otro chatbot.').replace('chatbot','<s style="text-decoration-thickness:3px;text-decoration-color:var(--blue)">chatbot</s>')}</h2>
    <p class="lead">{t('Hanno bisogno di qualcuno che risponda sempre, che conosca i loro servizi, i loro orari, i loro clienti, e che faccia davvero il lavoro: prenotare, qualificare, ricordare, richiamare.','Necesitan a alguien que responda siempre, que conozca sus servicios, sus horarios, sus clientes, y que haga realmente el trabajo: reservar, calificar, recordar, volver a llamar.')}</p>
    <p class="lead">{t('Noi costruiamo quel qualcuno. Software proprietari, progettati in Italia, che si integrano dove il lavoro succede e restano invisibili finché non servono.','Nosotros construimos ese alguien. Software propio, diseñado en Italia, que se integra donde ocurre el trabajo y permanece invisible hasta que hace falta.')}</p>
    {video_slot('manifesto-odyra')}
  </div>
  <div class="grid" style="gap:16px">
    <div class="card rv">{ic('bell')}<h3>{t('Sempre presente','Siempre presente')}</h3><p>{t('L\'AI di Odyra risponde quando le persone non possono.','La IA de Odyra responde cuando las personas no pueden.')}</p></div>
    <div class="card rv">{ic('plug')}<h3>{t('Dentro i tuoi strumenti','Dentro de tus herramientas')}</h3><p>{t('Lavora nel gestionale e nel CRM che usi già.','Trabaja en el software de gestión y el CRM que ya usas.')}</p></div>
    <div class="card rv">{ic('layers')}<h3>{t('Software proprietario','Software propio')}</h3><p>{t('Prodotti sviluppati e posseduti da Odyra, su una piattaforma che cresce con ogni nuovo verticale.','Productos desarrollados y propiedad de Odyra, sobre una plataforma que crece con cada nuevo vertical.')}</p></div>
  </div>
</div></section>

<section class="dark"><div class="wrap">
  <div class="sec-h"><span class="eyebrow">{t('Servizi','Servicios')}</span><h2>{t('La stessa tecnologia, dentro software house e grandi aziende.','La misma tecnología, dentro de software houses y grandes empresas.')}</h2></div>
  <div class="grid g4">
    <a class="card rv" href="{url('software-house')}">{ic('handshake')}<h3>{t('AI white-label','IA white-label')}</h3><p>{t('Agenti AI con il marchio del partner, integrati nel suo gestionale, con revenue share già pronto.','Agentes IA con la marca del socio, integrados en su software, con revenue share listo.')}</p></a>
    <a class="card rv" href="{url('enterprise')}">{ic('cog')}<h3>{t('Progetti enterprise','Proyectos enterprise')}</h3><p>{t('Agenti e automazioni su misura per vendite, customer service e back office.','Agentes y automatizaciones a medida para ventas, atención al cliente y back office.')}</p></a>
    <a class="card rv" href="{url('tecnologia')}#whatsapp">{ic('chat')}<h3>{t('Infrastruttura WhatsApp Business','Infraestructura WhatsApp Business')}</h3><p>{t('Numeri, template e gestione come Tech Provider Meta tramite Vonage.','Números, plantillas y gestión como Tech Provider de Meta a través de Vonage.')}</p></a>
    <a class="card rv" href="{url('tecnologia')}#conformita">{ic('shield')}<h3>{t('Conformità AI e privacy','Cumplimiento de IA y privacidad')}</h3><p>{t('Progettazione nel perimetro di AI Act e GDPR, per settori regolati.','Diseño dentro del perímetro del AI Act y el RGPD, para sectores regulados.')}</p></a>
  </div>
</div></section>

<section><div class="wrap">
  <div class="sec-h"><span class="eyebrow">{t('Casi studio','Casos de éxito')}</span><h2>{t('Due clienti, due prodotti, risultati reali.','Dos clientes, dos productos, resultados reales.')}</h2></div>
  <div class="grid g2">
    <a class="card rv" href="{url('casi')}#boss"><img class="boss-logo" src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers" style="width:64px;height:64px;border-radius:12px"><h3>BOSS — {t('l\'AI dentro il gestionale dei saloni','la IA dentro el software de los salones')}</h3><p>{t('GoAgent, l\'agente AI che BOSS offre ai saloni col proprio marchio. In produzione da giugno 2026: 262 chiamate gestite in 15 giorni nel salone pilota.','GoAgent, el agente IA que BOSS ofrece a los salones con su marca. En producción desde junio de 2026: 262 llamadas gestionadas en 15 días en el salón piloto.')}</p></a>
    <a class="card rv" href="{url('casi')}#global-trading"><span class="wordmark" style="margin-bottom:16px">Global Trading<small>Gruppo Colzani · Sportit.com</small></span><h3>{t('L\'agente commerciale che non dorme mai','El agente comercial que nunca duerme')}</h3><p>{t('Primo contatto sotto il minuto e capacità da 10 a 1.000 chiamate allo stesso costo, indipendente dall\'organico.','Primer contacto en menos de un minuto y capacidad de 10 a 1.000 llamadas al mismo coste, independiente de la plantilla.')}</p></a>
  </div>
</div></section>

<div class="claims" aria-hidden="true"><div>{mq}</div></div>

{cta()}
'''
    return layout('home', t('Odyra System — Software AI proprietari per chi non può perdere un cliente', 'Odyra System — Software de IA propio para quien no puede perder un cliente'),
        t('Odyra sviluppa software AI proprietari: agenti vocali e WhatsApp, agente commerciale, HAKO. Integrati nei gestionali, in produzione in Italia.', 'Odyra desarrolla software de IA propio: agentes de voz y WhatsApp, agente comercial, HAKO. Integrados en el software de gestión, en producción en Italia.'), body)

# ───────────────────────── GRUPPO ─────────────────────────
def page_gruppo():
    body = f'''
<section class="page-hero solo"><div class="wrap"><div>
  <span class="eyebrow">{t('Il gruppo','El grupo')}</span>
  <h1>{t('Il gruppo europeo dei software AI verticali.','El grupo europeo del software de IA vertical.')}</h1>
  <p class="lead">{t('Odyra è un gruppo tecnologico milanese che sviluppa e possiede software di intelligenza artificiale: agenti vocali, agenti conversazionali, piattaforme e prodotti verticali che lavorano dentro le aziende, 24 ore su 24.','Odyra es un grupo tecnológico milanés que desarrolla y posee software de inteligencia artificial: agentes de voz, agentes conversacionales, plataformas y productos verticales que trabajan dentro de las empresas, 24 horas al día.')}</p>
</div></div></section>
<section><div class="wrap grid g2" style="gap:28px">
  <div class="card rv">{ic('bolt')}<h3>{t('Missione','Misión')}</h3><p>{t('Dare a ogni azienda, dal singolo salone al gruppo industriale, una forza di lavoro AI affidabile, integrata e misurabile.','Dar a cada empresa, del salón individual al grupo industrial, una fuerza de trabajo de IA fiable, integrada y medible.')}</p></div>
  <div class="card rv">{ic('globe')}<h3>{t('Visione','Visión')}</h3><p>{t('Diventare il gruppo europeo di riferimento per i software AI verticali: un portafoglio di prodotti proprietari, ciascuno leader nel proprio mercato, su un\'unica infrastruttura condivisa.','Convertirnos en el grupo europeo de referencia del software de IA vertical: una cartera de productos propios, cada uno líder en su mercado, sobre una única infraestructura compartida.')}</p></div>
</div></section>
<section class="alt"><div class="wrap">
  <div class="sec-h"><span class="eyebrow">{t('In 30 secondi','En 30 segundos')}</span><h2>{t('Chiudiamo il vuoto di chi non risponde.','Cerramos el vacío de quien no responde.')}</h2>
  <p class="lead">{t('Ogni giorno le aziende perdono chiamate, lead e clienti perché nessuno risponde in tempo. Odyra sviluppa software proprietari che chiudono questo vuoto: agenti AI che parlano al telefono e su WhatsApp, prenotano direttamente nel gestionale, richiamano un contatto in meno di un minuto e scalano da dieci a mille conversazioni senza aggiungere personale.','Cada día las empresas pierden llamadas, leads y clientes porque nadie responde a tiempo. Odyra desarrolla software propio que cierra ese vacío: agentes de IA que hablan por teléfono y por WhatsApp, reservan directamente en el software, vuelven a llamar a un contacto en menos de un minuto y escalan de diez a mil conversaciones sin añadir personal.')}</p></div>
  <div class="grid g3">
    <div class="card rv">{ic('layers')}<h3>{t('Una piattaforma, molti prodotti','Una plataforma, muchos productos')}</h3><p>{t('Oltre 18 mesi di sviluppo di un\'infrastruttura proprietaria: la base che permette di lanciare nuovi prodotti e nuovi verticali senza ripartire da zero.','Más de 18 meses de desarrollo de una infraestructura propia: la base que permite lanzar nuevos productos y verticales sin partir de cero.')}</p></div>
    <div class="card rv">{ic('globe')}<h3>{t('Italia e Spagna','Italia y España')}</h3><p>{t('Sede a Milano. Prodotti già in produzione in Italia, in estensione a nuovi mercati e nuovi verticali.','Sede en Milán. Productos ya en producción en Italia, en expansión a nuevos mercados y verticales.')}</p></div>
    <div class="card rv">{ic('chart')}<h3>{t('Risultati, non architetture','Resultados, no arquitecturas')}</h3><p>{t('Misuriamo chiamate gestite, prenotazioni e tempi di risposta. È di questo che parliamo con i clienti.','Medimos llamadas gestionadas, reservas y tiempos de respuesta. De eso hablamos con los clientes.')}</p></div>
  </div>
</div></section>
<section><div class="wrap">
  <div class="sec-h"><span class="eyebrow">{t('Il portafoglio','La cartera')}</span><h2>{t('Prodotti con identità propria, sotto un solo marchio.','Productos con identidad propia, bajo una sola marca.')}</h2></div>
  <div class="grid g3">
    <a class="card rv" href="{url('voce')}" style="border-top:5px solid var(--c-voce)">{goagent_wm(True)}<h3>{t('Agenti AI vocali e WhatsApp','Agentes IA de voz y WhatsApp')}</h3><p>{t('Receptionist AI per le attività che vivono di appuntamenti.','Recepcionista IA para negocios que viven de citas.')}</p></a>
    <a class="card rv" href="{url('commerciale')}" style="border-top:5px solid var(--c-comm)"><h3>{t('Agente commerciale AI','Agente comercial IA')}</h3><p>{t('Speed-to-lead per chi fa lead generation.','Speed-to-lead para quien hace generación de leads.')}</p></a>
    <a class="card rv" href="{url('hako')}" style="border-top:5px solid var(--c-hako)"><img src="/assets/logos/hako.png" alt="HAKO" style="height:30px;width:auto"><h3 style="margin-top:12px">{t('Gestione pacchi in portineria','Gestión de paquetes en conserjería')}</h3><p>{t('Avvisi multicanale e multilingua per i condomini.','Avisos multicanal y multilingüe para vecinos.')}</p></a>
  </div>
</div></section>
{cta()}'''
    return layout('gruppo', t('Il gruppo — Odyra System', 'El grupo — Odyra System'), t('Missione, visione e portafoglio di Odyra: software AI proprietari su un\'unica piattaforma, da Milano all\'Europa.', 'Misión, visión y cartera de Odyra: software de IA propio sobre una única plataforma, de Milán a Europa.'), body)

# ───────────────────────── VOCE ─────────────────────────
def page_voce():
    ben = [
        (t('Nessuna chiamata persa', 'Ninguna llamada perdida'), t('Il telefono risponde anche quando lo staff è occupato o il negozio è chiuso', 'El teléfono responde aunque el equipo esté ocupado o el local cerrado'), 'phone'),
        (t('Agenda piena', 'Agenda llena'), t('Le prenotazioni arrivano a qualsiasi ora, direttamente nel gestionale', 'Las reservas llegan a cualquier hora, directamente en el software'), 'cal'),
        (t('Meno lavoro ripetitivo', 'Menos trabajo repetitivo'), t('Lo staff smette di rispondere sempre alle stesse domande', 'El equipo deja de responder siempre a las mismas preguntas'), 'user'),
        (t('Integrazione nativa', 'Integración nativa'), t('Nessun nuovo software da imparare: lavora dentro quello che c\'è già', 'Ningún software nuevo que aprender: trabaja dentro de lo que ya hay'), 'plug'),
        (t('Numero invariato', 'Número sin cambios'), t('L\'attività mantiene il suo numero di telefono', 'El negocio mantiene su número de teléfono'), 'phone'),
        (t('Attivazione rapida', 'Activación rápida'), t('Onboarding guidato e configurazione automatica a partire dal gestionale', 'Onboarding guiado y configuración automática a partir del software'), 'bolt'),
    ]
    bh = ''.join(f'<div class="card rv">{ic(i)}<h3>{a}</h3><p>{b}</p></div>' for a, b, i in ben)
    body = f'''
<section class="page-hero" style="--hero-c:rgba(59,130,246,.22)"><div class="wrap">
  <div>
    <span class="pill-logo"><i style="background:var(--c-voce)"></i>{t('Prodotto · Agenti AI vocali e WhatsApp','Producto · Agentes IA de voz y WhatsApp')}</span>
    <h1>{t('Non perdere più <span class="grad">una chiamata.</span>','No pierdas ni <span class="grad">una llamada más.</span>')}</h1>
    <p class="lead">{t('La receptionist AI di Odyra risponde a ogni chiamata e a ogni messaggio WhatsApp, giorno e notte, e prenota direttamente nel gestionale dell\'azienda.','La recepcionista IA de Odyra responde a cada llamada y a cada mensaje de WhatsApp, de día y de noche, y reserva directamente en el software de la empresa.')}</p>
    <div class="cta" style="display:flex;gap:14px;flex-wrap:wrap;margin-top:30px"><a class="btn btn-p" href="{url('contatti')}?interesse=voce">{t('Richiedi una demo','Solicita una demo')}</a><a class="btn btn-o" href="#cosa-fa">{t('Cosa fa','Qué hace')}</a></div>
  </div>
  {call_demo()}
</div></section>

<section id="cosa-fa"><div class="wrap grid g2" style="gap:56px;align-items:start">
  <div><span class="eyebrow">{t('Cosa fa','Qué hace')}</span><h2>{t('Fa davvero il lavoro: prenota, sposta, ricorda.','Hace realmente el trabajo: reserva, mueve, recuerda.')}</h2>
  <ul class="checks">
    <li>{t('Risponde al telefono con voce naturale in italiano e su WhatsApp, 24/7, anche in contemporanea su più conversazioni.','Responde al teléfono con voz natural y en WhatsApp, 24/7, incluso en varias conversaciones a la vez.')}</li>
    <li>{t('Prenota, sposta e cancella appuntamenti in tempo reale, leggendo servizi, operatori, turni e disponibilità.','Reserva, mueve y cancela citas en tiempo real, leyendo servicios, operarios, turnos y disponibilidad.')}</li>
    <li>{t('Conferma e ricorda gli appuntamenti con notifiche WhatsApp automatiche.','Confirma y recuerda las citas con notificaciones automáticas de WhatsApp.')}</li>
    <li>{t('Risponde alle domande su servizi, prezzi e orari a partire dalla base di conoscenza dell\'attività.','Responde a preguntas sobre servicios, precios y horarios a partir de la base de conocimiento del negocio.')}</li>
    <li>{t('Passa la conversazione a una persona del team quando serve.','Pasa la conversación a una persona del equipo cuando hace falta.')}</li>
    <li>{t('Mostra al titolare tutto in una dashboard: chiamate, prenotazioni, report, registrazioni.','Muestra al titular todo en un panel: llamadas, reservas, informes, grabaciones.')}</li></ul></div>
  <div>
    <div class="wa rv" aria-label="{t('Simulazione di conversazione WhatsApp','Simulación de conversación de WhatsApp')}">
      <div class="wa-h"><img src="/assets/logos/whatsapp.svg" alt="WhatsApp"><div><b>Salone Aurora</b><small>{t('account aziendale','cuenta empresarial')}</small></div></div>
      <div class="b out">{t('Ciao, posso spostare l\'appuntamento di domani?','Hola, ¿puedo mover la cita de mañana?')}<em>21:52</em></div>
      <div class="b in">{t('Certo Marta. Domani hai taglio alle 10:00. Preferisci giovedì alle 11:30 o venerdì alle 9:00?','Claro, Marta. Mañana tienes corte a las 10:00. ¿Prefieres el jueves a las 11:30 o el viernes a las 9:00?')}<em>21:52</em></div>
      <div class="b out">{t('Giovedì alle 11:30.','El jueves a las 11:30.')}<em>21:53</em></div>
      <div class="b in">{t('Fatto: giovedì 11:30 con Giulia. Ti ricordo l\'appuntamento il giorno prima. ✔','Hecho: jueves 11:30 con Giulia. Te recuerdo la cita el día anterior. ✔')}<em>21:53</em></div>
    </div>
    <p class="tag-ex">{t('Simulazione illustrativa','Simulación ilustrativa')}</p>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="sec-h"><span class="eyebrow">{t('Perché sceglierlo','Por qué elegirlo')}</span><h2>{t('Quello che cambia per l\'attività.','Lo que cambia para el negocio.')}</h2></div>
  <div class="grid g3">{bh}</div>
</div></section>

<section><div class="wrap grid g2" style="gap:48px;align-items:center">
  <div class="rv"><span class="eyebrow">{t('Per chi','Para quién')}</span><h2>{t('Per ogni attività che vive di appuntamenti.','Para cada negocio que vive de citas.')}</h2>
    <p class="lead">{t('Saloni, centri estetici, studi dentistici, cliniche veterinarie, centri sportivi. Distribuito tramite i gestionali di settore, con il loro marchio.','Salones, centros de estética, clínicas dentales, clínicas veterinarias, centros deportivos. Distribuido a través del software de gestión del sector, con su marca.')}</p></div>
  <div class="card rv" style="background:linear-gradient(160deg,#F4F0FF,#fff);border-color:#E3DAFF">
    <div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap">{goagent_wm()}<span style="color:var(--muted)">×</span><img class="boss-logo" src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers" style="width:68px;height:68px;border-radius:14px"></div>
    <h3 style="margin-top:20px">{t('GoAgent: l\'agente AI del gestionale BOSS','GoAgent: el agente IA del software BOSS')}</h3>
    <p>{t('Il prodotto Odyra alimenta GoAgent, che BOSS offre ai saloni della rete GoWeb. In produzione da giugno 2026, con 262 chiamate gestite in 15 giorni nel salone pilota.','El producto de Odyra alimenta GoAgent, que BOSS ofrece a los salones de la red GoWeb. En producción desde junio de 2026, con 262 llamadas gestionadas en 15 días en el salón piloto.')}</p>
    <p style="margin-top:14px"><a class="btn btn-o btn-sm" href="{url('casi')}#boss">{t('Leggi il caso studio','Lee el caso de éxito')}</a></p>
  </div>
</div></section>

{audio_slot()}

<section class="alt"><div class="wrap">
  <div class="card rv" style="display:flex;gap:22px;align-items:center;flex-wrap:wrap;justify-content:space-between;background:#fff8e1;border-color:#f6e2a2"><div style="max-width:60ch"><span class="badge soon">{t('In arrivo','Próximamente')}</span><h3 style="margin-top:12px">Retention AI</h3><p>{t('Il modulo che richiama automaticamente i clienti che non tornano da tempo, al telefono o su WhatsApp, e li riporta in agenda.','El módulo que vuelve a llamar automáticamente a los clientes que no regresan desde hace tiempo, por teléfono o WhatsApp, y los devuelve a la agenda.')}</p></div></div>
</div></section>
{cta(interesse='voce')}'''
    return layout('voce', t('Agenti AI vocali e WhatsApp — Odyra System', 'Agentes IA de voz y WhatsApp — Odyra System'), t('La receptionist AI che risponde al telefono e su WhatsApp 24/7 e prenota nel gestionale. Per saloni, studi, cliniche e centri sportivi.', 'La recepcionista IA que responde al teléfono y por WhatsApp 24/7 y reserva en tu software. Para salones, clínicas y centros deportivos.'), body)

# ───────────────────────── COMMERCIALE ─────────────────────────
def page_comm():
    steps = [
        (t('Il lead compila un modulo','El lead rellena un formulario'), t('Da campagne Meta, sito o landing page.','Desde campañas de Meta, web o landing page.')),
        (t('Messaggio di benvenuto su WhatsApp','Mensaje de bienvenida por WhatsApp'), t('Arriva subito, appena il contatto viene registrato.','Llega al instante, en cuanto se registra el contacto.')),
        (t('Chiamata entro 60 secondi','Llamada en menos de 60 segundos'), t('L\'agente AI lo qualifica con domande strutturate su bisogno, budget e tempi.','El agente IA lo califica con preguntas estructuradas sobre necesidad, presupuesto y plazos.')),
        (t('Appuntamento nel calendario','Cita en el calendario'), t('Se il lead è in target, l\'appuntamento finisce direttamente nel calendario del commerciale, con conferma su WhatsApp.','Si el lead encaja, la cita va directamente al calendario del comercial, con confirmación por WhatsApp.')),
        (t('Se non risponde, riprova','Si no contesta, reintenta'), t('L\'agente richiama negli orari giusti e lo recupera su WhatsApp.','El agente vuelve a llamar en los horarios adecuados y lo recupera por WhatsApp.')),
        (t('Esito scritto nel CRM','Resultado escrito en el CRM'), t('Ogni esito viene registrato nel CRM dell\'azienda.','Cada resultado queda registrado en el CRM de la empresa.')),
    ]
    sh = ''.join(f'<li class="rv"><div><h3>{a}</h3><p>{b}</p></div></li>' for a, b in steps)
    ben = [
        ('bolt', t('Speed-to-lead da ore a secondi','Speed-to-lead de horas a segundos'), t('7 giorni su 7, anche di notte e nei festivi.','7 días a la semana, también de noche y festivos.')),
        ('chart', t('Da 10 a 1.000 chiamate','De 10 a 1.000 llamadas'), t('La capacità non dipende dall\'organico: nessuna assunzione.','La capacidad no depende de la plantilla: sin contrataciones.')),
        ('shield', t('Qualità costante','Calidad constante'), t('Ogni lead riceve la stessa qualificazione, dal primo all\'ultimo.','Cada lead recibe la misma calificación, del primero al último.')),
        ('chat', t('Nessun lead perso','Ningún lead perdido'), t('Chi non risponde al telefono rientra da WhatsApp.','Quien no contesta al teléfono vuelve por WhatsApp.')),
        ('layers', t('Più valore dalla stessa spesa','Más valor del mismo gasto'), t('I contatti delle campagne vengono lavorati tutti, subito.','Todos los contactos de las campañas se trabajan, de inmediato.')),
        ('plug', t('Dentro il tuo CRM','Dentro de tu CRM'), t('Calendario e CRM aziendali sempre aggiornati.','Calendario y CRM de la empresa siempre actualizados.')),
    ]
    bh = ''.join(f'<div class="card rv">{ic(i)}<h3>{a}</h3><p>{b}</p></div>' for i, a, b in ben)
    body = f'''
<section class="page-hero" style="--hero-c:rgba(124,92,252,.22)"><div class="wrap">
  <div>
    <span class="pill-logo"><i style="background:var(--c-comm)"></i>{t('Prodotto · Agente commerciale AI','Producto · Agente comercial IA')}</span>
    <h1>{t('Chi arriva primo vende.<br><span class="grad">Odyra arriva primo.</span>','Quien llega primero vende.<br><span class="grad">Odyra llega primero.</span>')}</h1>
    <p class="lead">{t('L\'agente commerciale di Odyra richiama ogni nuovo lead in meno di un minuto, lo qualifica al telefono in italiano e fissa l\'appuntamento con il team vendite.','El agente comercial de Odyra llama a cada nuevo lead en menos de un minuto, lo califica por teléfono y fija la cita con el equipo de ventas.')}</p>
    <div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:30px"><a class="btn btn-p" href="{url('contatti')}?interesse=commerciale">{t('Richiedi una demo','Solicita una demo')}</a><a class="btn btn-o" href="{url('casi')}#global-trading">{t('Il caso Global Trading','El caso Global Trading')}</a></div>
  </div>
  <div class="device rv" style="text-align:center">
    <p class="eyebrow" style="justify-content:center">{t('Tempo al primo contatto','Tiempo hasta el primer contacto')}</p>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
      <div style="border:1px solid var(--line);border-radius:16px;padding:20px 10px"><small style="color:var(--muted)">{t('Senza Odyra','Sin Odyra')}</small><b style="display:block;font:600 2.1rem var(--display);color:#B91C1C;margin-top:6px">{t('ore','horas')}</b></div>
      <div style="border:2px solid var(--c-comm);border-radius:16px;padding:20px 10px;background:#F6F3FF"><small style="color:var(--c-comm);font-weight:700">Odyra</small><b style="display:block;font:600 2.1rem var(--display);color:var(--ink);margin-top:6px">&lt;60 s</b></div>
    </div>
    <div class="wave" aria-hidden="true">{''.join('<i style="animation-delay:%.2fs;background:linear-gradient(var(--c-comm),#4C34C9)"></i>' % (i*0.07) for i in range(26))}</div>
    <p class="tag-ex" style="margin-top:0">{t('Ogni nuovo lead richiamato in meno di un minuto','Cada nuevo lead llamado en menos de un minuto')}</p>
  </div>
</div></section>

<section><div class="wrap grid g2" style="gap:64px;align-items:start">
  <div><span class="eyebrow">{t('Come funziona','Cómo funciona')}</span><h2>{t('Dal modulo all\'appuntamento, in sei passi.','Del formulario a la cita, en seis pasos.')}</h2>
    <p class="lead">{t('Nessun lead aspetta. Nessun lead viene dimenticato.','Ningún lead espera. Ningún lead se olvida.')}</p>
    <div style="margin-top:28px;display:flex;gap:18px;align-items:center;flex-wrap:wrap"><img src="/assets/logos/meta.svg" alt="Meta" style="height:26px"><img src="/assets/logos/whatsapp.svg" alt="WhatsApp" style="height:28px"><span style="color:var(--muted);font-size:.9rem">{t('Campagne Meta e conferme su WhatsApp','Campañas de Meta y confirmaciones por WhatsApp')}</span></div></div>
  <ol class="steps">{sh}</ol>
</div></section>

<section class="alt"><div class="wrap">
  <div class="sec-h"><span class="eyebrow">{t('Perché sceglierlo','Por qué elegirlo')}</span><h2>{t('Più valore dalla stessa spesa pubblicitaria.','Más valor del mismo gasto publicitario.')}</h2></div>
  <div class="grid g3">{bh}</div>
</div></section>

<section><div class="wrap grid g2" style="gap:48px;align-items:center">
  <div class="rv"><span class="eyebrow">{t('Per chi','Para quién')}</span><h2>{t('Per chi vive di lead.','Para quien vive de leads.')}</h2>
    <ul class="checks"><li>{t('Aziende con campagne di lead generation','Empresas con campañas de generación de leads')}</li><li>{t('Reti commerciali e franchising','Redes comerciales y franquicias')}</li><li>{t('E-commerce','E-commerce')}</li><li>{t('Agenzie di marketing','Agencias de marketing')}</li></ul></div>
  <div class="card rv"><span class="wordmark">Global Trading<small>Gruppo Colzani · Sportit.com</small></span><h3 style="margin-top:18px">{t('Dieci chiamate o mille, stesso team.','Diez llamadas o mil, el mismo equipo.')}</h3><p>{t('Primo contatto sotto il minuto e capacità da 10 a 1.000 chiamate allo stesso costo. La collaborazione prosegue con l\'automazione del customer service email per i marketplace.','Primer contacto en menos de un minuto y capacidad de 10 a 1.000 llamadas al mismo coste. La colaboración continúa con la automatización del servicio de atención por e-mail para marketplaces.')}</p><p style="margin-top:14px"><a class="btn btn-o btn-sm" href="{url('casi')}#global-trading">{t('Leggi il caso studio','Lee el caso de éxito')}</a></p></div>
</div></section>
{cta(interesse='commerciale')}'''
    return layout('commerciale', t('Agente commerciale AI — Odyra System', 'Agente comercial IA — Odyra System'), t('Richiama ogni nuovo lead in meno di un minuto, lo qualifica al telefono e fissa l\'appuntamento nel calendario del team vendite.', 'Llama a cada nuevo lead en menos de un minuto, lo califica por teléfono y fija la cita en el calendario del equipo de ventas.'), body)

# ───────────────────────── HAKO ─────────────────────────
def page_hako():
    body = f'''
<section class="page-hero" style="--hero-c:rgba(0,174,239,.25)"><div class="wrap">
  <div>
    <img src="/assets/logos/hako.png" alt="HAKO" style="height:54px;width:auto;margin-bottom:26px">
    <h1>{t('Ogni pacco in portineria, <span class="grad">ogni condomino avvisato.</span>','Cada paquete en conserjería, <span class="grad">cada vecino avisado.</span>')}</h1>
    <p class="lead">{t('HAKO registra il pacco con una foto, avvisa il destinatario su WhatsApp, SMS o e-mail nella sua lingua e chiude la consegna con un codice di ritiro.','HAKO registra el paquete con una foto, avisa al destinatario por WhatsApp, SMS o e-mail en su idioma y cierra la entrega con un código de recogida.')}</p>
    <div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:30px"><a class="btn btn-p" href="{url('contatti')}?interesse=hako">{t('Richiedi una demo','Solicita una demo')}</a><a class="btn btn-o" href="https://hakocondomini.com" rel="noopener">{t('Vai al sito HAKO','Ir al sitio de HAKO')} ↗</a></div>
  </div>
  <div class="device rv" style="--c:var(--c-hako)">
    <div class="dv-top"><img src="/assets/logos/whatsapp.svg" alt="WhatsApp" style="width:34px;height:34px"><div><b>HAKO</b><small>{t('Account aziendale','Cuenta empresarial')}</small></div></div>
    <div class="msgs" style="min-height:0;padding-top:16px"><div class="msg ai" style="animation-delay:.5s">📦 HAKO: {t('Marta, hai ricevuto un pacco da DHL. Codice: 4821. Ritiralo in portineria.','Marta, has recibido un paquete de DHL. Código: 4821. Recógelo en conserjería.')}</div></div>
    <div class="confirm" style="animation-delay:1.8s;background:#E6F7FE;border-color:#B5E4F8;color:#0D2F6E"><span style="font-size:1.4rem">🔑</span><div><b style="color:#0D2F6E">{t('Ritiro con codice','Recogida con código')}</b>{t('Codice QR valido in un secondo','Código QR válido en un segundo')}</div></div>
    <p class="tag-ex">{t('Esempio illustrativo','Ejemplo ilustrativo')}</p>
  </div>
</div></section>

<section><div class="wrap">
  <div class="sec-h"><span class="eyebrow">{t('Come funziona','Cómo funciona')}</span><h2>{t('Tre passaggi, nessun registro cartaceo.','Tres pasos, ningún registro en papel.')}</h2><p class="lead">{t('HAKO è il programma della portineria che sostituisce il quaderno dei pacchi: il portinaio registra il pacco, HAKO avvisa il condomino da solo e tiene lo storico di ogni consegna.','HAKO es el programa de la conserjería que sustituye al cuaderno de paquetes: el conserje registra el paquete, HAKO avisa al vecino solo y guarda el historial de cada entrega.')}</p></div>
  <div class="grid g3">
    <div class="card rv">{ic('box')}<h3>1. {t('Il portinaio fotografa il pacco','El conserje fotografía el paquete')}</h3><p>{t('HAKO legge destinatario e corriere dall\'etichetta, oppure scansiona il codice a barre. Il portinaio controlla e conferma.','HAKO lee destinatario y transportista de la etiqueta, o escanea el código de barras. El conserje revisa y confirma.')}</p></div>
    <div class="card rv">{ic('bell')}<h3>2. {t('Il condomino riceve l\'avviso','El vecino recibe el aviso')}</h3><p>{t('Un messaggio con corriere, condominio e codice di ritiro, nella lingua che ha scelto.','Un mensaje con transportista, comunidad y código de recogida, en el idioma que ha elegido.')}</p></div>
    <div class="card rv">{ic('shield')}<h3>3. {t('Il ritiro si chiude con il codice','La recogida se cierra con el código')}</h3><p>{t('Il condomino mostra il codice, il portinaio registra la consegna e arriva la conferma. Lo storico resta consultabile.','El vecino muestra el código, el conserje registra la entrega y llega la confirmación. El historial queda consultable.')}</p></div>
  </div>
</div></section>

<section class="alt"><div class="wrap">
  <div class="sec-h"><span class="eyebrow">{t('Canali','Canales')}</span><h2>{t('Come arriva l\'avviso al condomino.','Cómo llega el aviso al vecino.')}</h2><p class="lead">{t('HAKO usa i servizi di messaggistica ufficiali. Tu non configuri niente: ci pensiamo noi.','HAKO usa los servicios de mensajería oficiales. Tú no configuras nada: nos encargamos nosotros.')}</p></div>
  <div class="grid g3">
    <div class="card rv"><img src="/assets/logos/whatsapp.svg" alt="WhatsApp" style="height:44px;width:auto"><h3>WhatsApp</h3><p>{t('L\'avviso arriva dal numero di HAKO, non dal telefono del portinaio, tramite la piattaforma WhatsApp Business di Meta, con messaggi approvati in ogni lingua.','El aviso llega desde el número de HAKO, no desde el teléfono del conserje, a través de la plataforma WhatsApp Business de Meta, con mensajes aprobados en cada idioma.')}</p></div>
    <div class="card rv">{ic('phone')}<h3>SMS</h3><p>{t('Per chi non usa WhatsApp e per la conferma di ritiro. Arriva sul numero del residente, senza app e senza connessione dati.','Para quien no usa WhatsApp y para la confirmación de recogida. Llega al número del residente, sin app y sin conexión de datos.')}</p></div>
    <div class="card rv">{ic('mail')}<h3>{t('E-mail','E-mail')}</h3><p>{t('Gli stessi dati, per chi preferisce la posta o non vuole dare il cellulare. Ogni residente sceglie il suo canale.','Los mismos datos, para quien prefiere el correo o no quiere dar el móvil. Cada residente elige su canal.')}</p></div>
  </div>
</div></section>

<section><div class="wrap grid g3">
  <div class="card rv">{ic('user')}<h3>{t('Per il portinaio','Para el conserje')}</h3><ul class="checks"><li>{t('Lettura dell\'etichetta con la fotocamera e scansione del codice a barre','Lectura de la etiqueta con la cámara y escaneo del código de barras')}</li><li>{t('Registra anche senza connessione e sincronizza appena torna la rete','Registra incluso sin conexión y sincroniza al volver la red')}</li><li>{t('Passaggio di consegne a fine turno','Relevo de turno al final de la jornada')}</li></ul></div>
  <div class="card rv">{ic('phone')}<h3>{t('Per il condomino','Para el vecino')}</h3><ul class="checks"><li>{t('Avviso su WhatsApp, SMS o e-mail, come preferisce','Aviso por WhatsApp, SMS o e-mail, como prefiera')}</li><li>{t('Codice QR di ritiro e delega a un\'altra persona','Código QR de recogida y delegación en otra persona')}</li><li>{t('Accesso con codice via SMS, senza password, senza app','Acceso con código por SMS, sin contraseña ni app')}</li></ul></div>
  <div class="card rv">{ic('chart')}<h3>{t('Per chi amministra','Para quien administra')}</h3><ul class="checks"><li>{t('Storico completo con foto, orari e chi ha ritirato','Historial completo con fotos, horas y quién recogió')}</li><li>{t('Solleciti automatici dopo i giorni che decidi tu','Recordatorios automáticos tras los días que decidas')}</li><li>{t('Residenti importati da file CSV o Excel','Residentes importados desde archivo CSV o Excel')}</li></ul></div>
</div></section>

<section class="dark"><div class="wrap">
  <div class="sec-h"><span class="eyebrow">{t('Dati e privacy','Datos y privacidad')}</span><h2>{t('I dati dei residenti restano sotto controllo.','Los datos de los residentes siguen bajo control.')}</h2></div>
  <div class="grid g4">
    <div class="card rv">{ic('server')}<h3>{t('Cancellazione automatica','Borrado automático')}</h3><p>{t('Foto e dati letti dall\'etichetta vengono cancellati dopo un periodo stabilito.','Fotos y datos leídos de la etiqueta se borran tras un periodo establecido.')}</p></div>
    <div class="card rv">{ic('shield')}<h3>GDPR</h3><p>{t('Esportazione e cancellazione dei dati su richiesta del residente.','Exportación y borrado de datos a petición del residente.')}</p></div>
    <div class="card rv">{ic('book')}<h3>{t('Registro operazioni','Registro de operaciones')}</h3><p>{t('Ogni azione resta registrata, con chi l\'ha fatta e quando.','Cada acción queda registrada, con quién la hizo y cuándo.')}</p></div>
    <div class="card rv">{ic('user')}<h3>{t('Accessi per ruolo','Accesos por rol')}</h3><p>{t('Portinaio, amministratore e condomino vedono solo ciò che serve.','Conserje, administrador y vecino ven solo lo necesario.')}</p></div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="sec-h"><span class="eyebrow">FAQ</span><h2>{t('Domande frequenti.','Preguntas frecuentes.')}</h2></div>
  <div class="grid g2">
    <div class="card"><h3>{t('Il condomino deve installare un\'app?','¿El vecino debe instalar una app?')}</h3><p>{t('No. Riceve l\'avviso sul canale che usa già e, per vedere i suoi pacchi, apre una pagina dal browser del telefono.','No. Recibe el aviso por el canal que ya usa y, para ver sus paquetes, abre una página en el navegador del móvil.')}</p></div>
    <div class="card"><h3>{t('Serve un\'attrezzatura speciale?','¿Hace falta equipo especial?')}</h3><p>{t('Basta un tablet o un computer con la fotocamera. HAKO si apre dal browser e funziona anche quando la connessione cade.','Basta una tablet o un ordenador con cámara. HAKO se abre desde el navegador y funciona incluso cuando se cae la conexión.')}</p></div>
    <div class="card"><h3>{t('Come si parte?','¿Cómo se empieza?')}</h3><p>{t('Ci mandi l\'elenco dei residenti in CSV o Excel, lo importiamo, creiamo gli accessi e si comincia dai pacchi di oggi.','Nos envías la lista de residentes en CSV o Excel, la importamos, creamos los accesos y se empieza con los paquetes de hoy.')}</p></div>
    <div class="card"><h3>{t('Quanto costa?','¿Cuánto cuesta?')}</h3><p>{t('Stiamo aprendo i primi stabili pilota con condizioni dedicate. Scrivici quanti condomini gestisci e ti mandiamo una proposta.','Estamos abriendo los primeros edificios piloto con condiciones dedicadas. Dinos cuántos vecinos gestionas y te enviamos una propuesta.')}</p></div>
  </div>
  <p style="margin-top:28px"><a class="btn btn-o" href="https://hakocondomini.com" rel="noopener">{t('Tutti i dettagli su hakocondomini.com','Todos los detalles en hakocondomini.com')} ↗</a></p>
</div></section>
{cta(t('Prova HAKO nel tuo stabile.','Prueba HAKO en tu edificio.'), t('Stiamo aprendo i primi stabili pilota. Ci racconti come lavorate oggi in portineria e prepariamo il resto.','Estamos abriendo los primeros edificios piloto. Cuéntanos cómo trabajáis hoy en conserjería y preparamos el resto.'), 'hako')}'''
    return layout('hako', t('HAKO — Gestione pacchi per condomini con portineria', 'HAKO — Gestión de paquetes para comunidades con conserjería'), t('HAKO registra il pacco con una foto e avvisa il condomino su WhatsApp, SMS o e-mail nella sua lingua. Prodotto del gruppo Odyra.', 'HAKO registra el paquete con una foto y avisa al vecino por WhatsApp, SMS o e-mail en su idioma. Producto del grupo Odyra.'), body)

# ───────────────────────── SOFTWARE HOUSE ─────────────────────────
def page_sh():
    inc = [
        ('plug', t('Integrato nel tuo gestionale','Integrado en tu software'), t('Un connettore dedicato collega il tuo software alla piattaforma, senza toccarne il cuore.','Un conector dedicado conecta tu software con la plataforma, sin tocar su núcleo.')),
        ('handshake', t('Marchio del partner','Marca del socio'), t('Agenti AI vocali e WhatsApp con il tuo logo, in interfacce sempre col tuo marchio.','Agentes IA de voz y WhatsApp con tu logo, en interfaces siempre con tu marca.')),
        ('user', t('Onboarding dei clienti','Onboarding de clientes'), t('Attivazione automatica a partire dal gestionale: i tuoi clienti partono in fretta.','Activación automática a partir del software: tus clientes arrancan rápido.')),
        ('chart', t('Dashboard per i titolari','Panel para los titulares'), t('Chiamate, prenotazioni, report e registrazioni, già pronti.','Llamadas, reservas, informes y grabaciones, ya listos.')),
        ('layers', t('Piattaforma di revenue share','Plataforma de revenue share'), t('Gestione dei ricavi condivisi pronta, senza costruire nulla.','Gestión de ingresos compartidos lista, sin construir nada.')),
        ('chat', t('WhatsApp Business gestito','WhatsApp Business gestionado'), t('Numeri, template e conversazioni gestiti da Odyra come Tech Provider Meta.','Números, plantillas y conversaciones gestionados por Odyra como Tech Provider de Meta.')),
    ]
    ih = ''.join(f'<div class="card rv">{ic(i)}<h3>{a}</h3><p>{b}</p></div>' for i, a, b in inc)
    body = f'''
<section class="page-hero"><div class="wrap">
  <div>
    <span class="eyebrow">{t('Per le software house','Para software houses')}</span>
    <h1>{t('Il tuo gestionale, <span class="grad">ora risponde.</span>','Tu software, <span class="grad">ahora responde.</span>')}</h1>
    <p class="lead">{t('AI white-label per gestionali verticali e SaaS: agenti vocali e WhatsApp con il tuo marchio, integrati nel tuo software. Tu porti i clienti, Odyra porta prodotto, tecnologia e gestione operativa.','IA white-label para software de gestión verticales y SaaS: agentes de voz y WhatsApp con tu marca, integrados en tu software. Tú aportas los clientes, Odyra aporta producto, tecnología y gestión operativa.')}</p>
    <div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:30px"><a class="btn btn-p" href="{url('contatti')}?interesse=software-house">{t('Diventa partner','Hazte socio')}</a><a class="btn btn-o" href="{url('casi')}#boss">{t('Il caso BOSS','El caso BOSS')}</a></div>
  </div>
  <div class="device rv" style="text-align:center">
    <p class="eyebrow" style="justify-content:center">{t('Il modello','El modelo')}</p>
    <div style="display:grid;gap:12px;font-weight:700;color:var(--ink)">
      <div style="padding:16px;border:1px solid var(--line);border-radius:14px;background:var(--paper)">{t('Il partner porta i clienti','El socio aporta los clientes')}</div>
      <div style="font-size:1.4rem;color:var(--blue)">+</div>
      <div style="padding:16px;border-radius:14px;background:linear-gradient(135deg,var(--blue),var(--blue-d));color:#fff">{t('Odyra porta prodotto, tecnologia e gestione','Odyra aporta producto, tecnología y gestión')}</div>
      <div style="font-size:1.4rem;color:var(--blue)">=</div>
      <div style="padding:16px;border:2px solid var(--blue);border-radius:14px">{t('Un nuovo servizio AI col tuo nome, a ricavo ricorrente','Un nuevo servicio IA con tu nombre, de ingreso recurrente')}</div>
    </div>
  </div>
</div></section>

<section><div class="wrap">
  <div class="sec-h"><span class="eyebrow">{t('Cosa include','Qué incluye')}</span><h2>{t('Tutto già pronto. Non devi costruire nulla.','Todo listo. No tienes que construir nada.')}</h2></div>
  <div class="grid g3">{ih}</div>
</div></section>

<section class="alt"><div class="wrap grid g2" style="gap:56px;align-items:center">
  <div class="rv"><span class="eyebrow">{t('Perché ora','Por qué ahora')}</span><h2>{t('I tuoi clienti chiedono AI. Non serve costruirla in casa.','Tus clientes piden IA. No hace falta construirla en casa.')}</h2>
    <ul class="checks"><li>{t('Un nuovo ricavo ricorrente, in abbonamento, per tutta la tua base clienti','Un nuevo ingreso recurrente, por suscripción, para toda tu base de clientes')}</li><li>{t('Formule flessibili: condivisione dei ricavi o licenza a volume','Fórmulas flexibles: reparto de ingresos o licencia por volumen')}</li><li>{t('Nessun team AI da assumere, nessuna infrastruttura da mantenere','Sin equipo de IA que contratar, sin infraestructura que mantener')}</li><li>{t('Tempi rapidi: un nuovo gestionale si collega con un connettore dedicato','Plazos rápidos: un nuevo software se conecta con un conector dedicado')}</li></ul></div>
  <div class="card rv" style="background:linear-gradient(160deg,#F4F0FF,#fff);border-color:#E3DAFF">
    <img class="boss-logo" src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers" style="width:72px;height:72px;border-radius:14px">
    <h3 style="margin-top:18px">{t('BOSS ha già scelto questa strada.','BOSS ya ha elegido este camino.')}</h3>
    <p>{t('Con GoAgent, BOSS ha aggiunto al gestionale GoWeb un servizio AI in abbonamento, pronto per l\'intera rete di circa 1.500 saloni.','Con GoAgent, BOSS ha añadido al software GoWeb un servicio de IA por suscripción, listo para toda la red de unos 1.500 salones.')}</p>
    <p style="margin-top:14px"><a class="btn btn-o btn-sm" href="{url('casi')}#boss">{t('Leggi il caso studio','Lee el caso de éxito')}</a></p></div>
</div></section>

<section><div class="wrap">
  <div class="sec-h"><span class="eyebrow">{t('Per chi','Para quién')}</span><h2>{t('Gestionali verticali e SaaS.','Software de gestión verticales y SaaS.')}</h2><p class="lead">{t('Saloni, centri estetici, studi dentistici, cliniche veterinarie, centri sportivi e ogni settore dove il lavoro ruota attorno agli appuntamenti.','Salones, centros de estética, clínicas dentales, clínicas veterinarias, centros deportivos y cualquier sector donde el trabajo gira en torno a las citas.')}</p></div>
</div></section>
{cta(t('Porta l\'AI nel tuo gestionale.','Lleva la IA a tu software.'), t('Parliamo di integrazione, formula commerciale e tempi.','Hablemos de integración, fórmula comercial y plazos.'), 'software-house')}'''
    return layout('software-house', t('Per le software house — AI white-label · Odyra System', 'Para software houses — IA white-label · Odyra System'), t('AI white-label per gestionali verticali e SaaS: agenti vocali e WhatsApp con il tuo marchio, integrati nel tuo software, con revenue share pronto.', 'IA white-label para software verticales y SaaS: agentes de voz y WhatsApp con tu marca, integrados en tu software, con revenue share listo.'), body)

# ───────────────────────── ENTERPRISE ─────────────────────────
def page_ent():
    amb = [
        ('chart', t('Vendite','Ventas'), t('Qualificazione dei lead, richiami, fissaggio appuntamenti, aggiornamento del CRM.','Calificación de leads, llamadas, fijación de citas, actualización del CRM.')),
        ('chat', 'Customer service', t('Voce, WhatsApp ed e-mail: risposte coerenti, con passaggio a una persona quando serve.','Voz, WhatsApp y e-mail: respuestas coherentes, con paso a una persona cuando hace falta.')),
        ('cog', 'Back office', t('Automazioni sui processi ripetitivi, tra i sistemi che l\'azienda usa già.','Automatizaciones en procesos repetitivos, entre los sistemas que la empresa ya usa.')),
        ('plug', t('Integrazione CRM ed ERP','Integración CRM y ERP'), t('Agenti che leggono e scrivono dove sono i dati.','Agentes que leen y escriben donde están los datos.')),
    ]
    ah = ''.join(f'<div class="card rv">{ic(i)}<h3>{a}</h3><p>{b}</p></div>' for i, a, b in amb)
    met = [
        (t('Analisi del processo','Análisis del proceso'), t('Partiamo dai flussi reali: dove si perdono chiamate, tempo e margine.','Partimos de los flujos reales: dónde se pierden llamadas, tiempo y margen.')),
        (t('Disegno dell\'agente','Diseño del agente'), t('Definiamo cosa deve fare, cosa sa, quando passa la mano a una persona.','Definimos qué debe hacer, qué sabe y cuándo cede el paso a una persona.')),
        (t('Integrazione','Integración'), t('Connettiamo CRM, ERP e gestionali tramite connettori dedicati.','Conectamos CRM, ERP y software de gestión mediante conectores dedicados.')),
        (t('Messa in produzione e misura','Puesta en producción y medición'), t('Dashboard con chiamate, esiti e tempi, per migliorare ogni settimana.','Panel con llamadas, resultados y tiempos, para mejorar cada semana.')),
    ]
    mh = ''.join(f'<li class="rv"><div><h3>{a}</h3><p>{b}</p></div></li>' for a, b in met)
    body = f'''
<section class="page-hero solo"><div class="wrap"><div>
  <span class="eyebrow">Enterprise</span>
  <h1>{t('Agenti e automazioni AI <span class="grad">disegnati sui tuoi processi.</span>','Agentes y automatizaciones IA <span class="grad">diseñados sobre tus procesos.</span>')}</h1>
  <p class="lead">{t('Per gruppi industriali e aziende con grandi volumi: progetti su misura su vendite, customer service e back office, integrati con CRM ed ERP.','Para grupos industriales y empresas con grandes volúmenes: proyectos a medida en ventas, atención al cliente y back office, integrados con CRM y ERP.')}</p>
  <div style="margin-top:30px"><a class="btn btn-p" href="{url('contatti')}?interesse=enterprise">{t('Parliamo del progetto','Hablemos del proyecto')}</a></div>
</div></div></section>
<section><div class="wrap"><div class="sec-h"><span class="eyebrow">{t('Ambiti','Ámbitos')}</span><h2>{t('Dove l\'AI fa lavoro vero.','Donde la IA hace trabajo real.')}</h2></div><div class="grid g4">{ah}</div></div></section>
<section class="alt"><div class="wrap grid g2" style="gap:64px;align-items:start">
  <div><span class="eyebrow">{t('Metodo di lavoro','Método de trabajo')}</span><h2>{t('Dal processo alla produzione, in quattro passi.','Del proceso a la producción, en cuatro pasos.')}</h2><p class="lead">{t('Sviluppiamo su una piattaforma proprietaria già in produzione: i tempi si accorciano e l\'affidabilità non è da dimostrare.','Desarrollamos sobre una plataforma propia ya en producción: los plazos se acortan y la fiabilidad no hay que demostrarla.')}</p></div>
  <ol class="steps">{mh}</ol>
</div></section>
<section><div class="wrap grid g2" style="gap:28px;align-items:stretch">
  <div class="card rv"><span class="wordmark">Global Trading<small>Gruppo Colzani · Sportit.com</small></span><h3 style="margin-top:18px">{t('Un caso enterprise: dai lead al customer service','Un caso enterprise: de los leads al servicio de atención')}</h3><p>{t('Dall\'agente commerciale che richiama ogni lead in meno di un minuto all\'automazione del customer service email per i marketplace.','Del agente comercial que llama a cada lead en menos de un minuto a la automatización del servicio de atención por e-mail para marketplaces.')}</p><p style="margin-top:14px"><a class="btn btn-o btn-sm" href="{url('casi')}#global-trading">{t('Leggi il caso studio','Lee el caso de éxito')}</a></p></div>
  <div class="card rv" id="conformita">{ic('shield')}<h3>{t('Conformità fin dal progetto','Cumplimiento desde el diseño')}</h3><p>{t('Progettiamo nel perimetro di AI Act e GDPR, con accordi su dati e cybersecurity e supporto alla documentazione.','Diseñamos dentro del perímetro del AI Act y el RGPD, con acuerdos sobre datos y ciberseguridad y apoyo a la documentación.')}</p><p style="margin-top:14px"><a class="btn btn-o btn-sm" href="{url('tecnologia')}#conformita">{t('Tecnologia e sicurezza','Tecnología y seguridad')}</a></p></div>
</div></section>
{cta(t('Hai un processo da automatizzare?','¿Tienes un proceso que automatizar?'), t('Raccontacelo: ti diciamo cosa si può fare e in quanto tempo.','Cuéntanoslo: te decimos qué se puede hacer y en cuánto tiempo.'), 'enterprise')}'''
    return layout('enterprise', t('Enterprise — Progetti AI su misura · Odyra System', 'Enterprise — Proyectos de IA a medida · Odyra System'), t('Agenti e automazioni AI su misura per vendite, customer service e back office, integrati con CRM ed ERP.', 'Agentes y automatizaciones IA a medida para ventas, atención al cliente y back office, integrados con CRM y ERP.'), body)

# ───────────────────────── CASI ─────────────────────────
def page_casi():
    body = f'''
<section class="page-hero solo"><div class="wrap"><div>
  <span class="eyebrow">{t('Casi studio','Casos de éxito')}</span>
  <h1>{t('Due clienti, due prodotti, <span class="grad">due modi di lavorare.</span>','Dos clientes, dos productos, <span class="grad">dos formas de trabajar.</span>')}</h1>
  <p class="lead">{t('Una partnership white-label con un gestionale nazionale e un agente commerciale per un gruppo e-commerce.','Una alianza white-label con un software de gestión nacional y un agente comercial para un grupo de e-commerce.')}</p>
</div></div></section>
<section><div class="wrap">
  <article class="case" id="boss">
    <div class="side rv"><img class="boss-logo" src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers" style="width:92px;height:92px;border-radius:18px;margin-bottom:22px"><span class="badge">{t('Partnership white-label','Alianza white-label')}</span><h3 style="margin-top:14px">BOSS</h3><p style="font-size:.93rem">Business Orientato ai Servizi per il Salone S.r.l. — {t('sviluppa GoWeb, uno dei gestionali più diffusi tra parrucchieri e centri estetici in Italia, con una rete di circa 1.500 saloni.','desarrolla GoWeb, uno de los software de gestión más extendidos entre peluquerías y centros de estética en Italia, con una red de unos 1.500 salones.')}</p>
      <div style="margin-top:22px">{goagent_wm()}</div>
      <div class="kpi"><div><b>262</b><span>{t('chiamate in 15 giorni','llamadas en 15 días')}</span></div><div><b>~1.500</b><span>{t('saloni nella rete','salones en la red')}</span></div></div></div>
    <div class="main rv"><h3>{t('L\'AI dentro il gestionale dei saloni','La IA dentro el software de los salones')}</h3>
      <dl>
        <div><dt>{t('La sfida','El reto')}</dt><dd>{t('I saloni perdono prenotazioni ogni giorno: il telefono squilla mentre lo staff lavora, i messaggi arrivano a negozio chiuso. BOSS voleva offrire ai propri clienti un assistente AI vero, integrato nel gestionale, senza costruirlo in casa.','Los salones pierden reservas cada día: el teléfono suena mientras el equipo trabaja, los mensajes llegan con el local cerrado. BOSS quería ofrecer a sus clientes un asistente de IA real, integrado en el software, sin construirlo en casa.')}</dd></div>
        <div><dt>{t('La soluzione','La solución')}</dt><dd>{t('Odyra ha costruito GoAgent, l\'agente AI che BOSS offre ai saloni col proprio marchio. Risponde al telefono e su WhatsApp 24/7, legge catalogo servizi, operatori e disponibilità di GoWeb e scrive le prenotazioni direttamente in agenda. Odyra ha realizzato anche l\'onboarding automatico dei saloni, la dashboard per i titolari e la piattaforma di gestione dei ricavi condivisi.','Odyra construyó GoAgent, el agente IA que BOSS ofrece a los salones con su marca. Responde al teléfono y por WhatsApp 24/7, lee el catálogo de servicios, operarios y disponibilidad de GoWeb y escribe las reservas directamente en la agenda. Odyra también ha realizado el onboarding automático de los salones, el panel para los titulares y la plataforma de gestión de ingresos compartidos.')}</dd></div>
        <div><dt>{t('Il risultato','El resultado')}</dt><dd>{t('In produzione da giugno 2026. Nel salone pilota, 262 chiamate gestite nei primi 15 giorni. BOSS ha aggiunto al proprio gestionale un servizio AI in abbonamento, pronto per l\'intera rete.','En producción desde junio de 2026. En el salón piloto, 262 llamadas gestionadas en los primeros 15 días. BOSS ha añadido a su software un servicio de IA por suscripción, listo para toda la red.')}</dd></div>
      </dl></div>
  </article>
  <article class="case" id="global-trading">
    <div class="side rv"><span class="wordmark" style="font-size:1.5rem;margin-bottom:22px">Global Trading<small>Gruppo Colzani · Sportit.com</small></span><span class="badge">{t('Agente commerciale AI','Agente comercial IA')}</span><h3 style="margin-top:14px">Global Trading S.r.l.</h3><p style="font-size:.93rem">{t('Il gruppo dietro Sportit.com, e-commerce e rete commerciale nel mondo dello sport.','El grupo detrás de Sportit.com, e-commerce y red comercial en el mundo del deporte.')}</p>
      <div class="kpi"><div><b>&lt;60 s</b><span>{t('al primo contatto','al primer contacto')}</span></div><div><b>10→1.000</b><span>{t('chiamate, stesso costo','llamadas, mismo coste')}</span></div></div></div>
    <div class="main rv"><h3>{t('L\'agente commerciale che non dorme mai','El agente comercial que nunca duerme')}</h3>
      <dl>
        <div><dt>{t('La sfida','El reto')}</dt><dd>{t('Ogni campagna genera centinaia di lead. Richiamarli tutti entro un minuto, in italiano e con la stessa qualità, non è possibile a mano; scalare significava assumere.','Cada campaña genera cientos de leads. Llamarlos a todos en un minuto, en italiano y con la misma calidad, no es posible a mano; escalar significaba contratar.')}</dd></div>
        <div><dt>{t('La soluzione','La solución')}</dt><dd>{t('Un agente commerciale AI: messaggio di benvenuto immediato su WhatsApp, chiamata entro pochi secondi, qualificazione strutturata, appuntamento fissato nel calendario del team con conferma su WhatsApp, esiti scritti nel CRM aziendale. La collaborazione prosegue con l\'automazione del customer service email per i marketplace.','Un agente comercial IA: mensaje de bienvenida inmediato por WhatsApp, llamada en pocos segundos, calificación estructurada, cita fijada en el calendario del equipo con confirmación por WhatsApp, resultados escritos en el CRM de la empresa. La colaboración continúa con la automatización del servicio de atención por e-mail para marketplaces.')}</dd></div>
        <div><dt>{t('Il risultato','El resultado')}</dt><dd>{t('Primo contatto sotto il minuto e capacità da 10 a 1.000 chiamate allo stesso costo, indipendente dall\'organico.','Primer contacto en menos de un minuto y capacidad de 10 a 1.000 llamadas al mismo coste, independiente de la plantilla.')}</dd></div>
      </dl></div>
  </article>
</div></section>
{cta()}'''
    return layout('casi', t('Casi studio — BOSS e Global Trading · Odyra System', 'Casos de éxito — BOSS y Global Trading · Odyra System'), t('GoAgent per BOSS e l\'agente commerciale per Global Trading: i casi studio di Odyra, con numeri reali.', 'GoAgent para BOSS y el agente comercial para Global Trading: los casos de éxito de Odyra, con números reales.'), body)

# ───────────────────────── TECNOLOGIA ─────────────────────────
def page_tech():
    items = [
        ('layers', 'Multi-tenant', t('Ogni azienda ha il proprio agente, i propri dati e la propria configurazione, isolati dagli altri, sulla stessa piattaforma.','Cada empresa tiene su propio agente, sus propios datos y su propia configuración, aislados de los demás, sobre la misma plataforma.')),
        ('plug', t('Integrazione a connettori','Integración por conectores'), t('Un nuovo gestionale si collega tramite un connettore dedicato, senza toccare il cuore della piattaforma: più veloce per il partner, più solido per tutti.','Un nuevo software se conecta mediante un conector dedicado, sin tocar el núcleo de la plataforma: más rápido para el socio, más sólido para todos.')),
        ('mic', t('Voce in tempo reale','Voz en tiempo real'), t('Conversazioni naturali in italiano con latenza sotto il secondo.','Conversaciones naturales con latencia inferior al segundo.')),
        ('brain', t('Conoscenza dell\'attività','Conocimiento del negocio'), t('Ogni agente risponde a partire dai servizi, dai prezzi e dalle regole dell\'azienda.','Cada agente responde a partir de los servicios, precios y reglas de la empresa.')),
        ('server', t('Infrastruttura privata','Infraestructura privada'), t('Voce e dati girano su infrastruttura dedicata e controllata da Odyra.','Voz y datos funcionan sobre infraestructura dedicada y controlada por Odyra.')),
        ('shield', t('Privacy e AI Act by design','Privacidad y AI Act desde el diseño'), t('Trattamento dei dati conforme al GDPR, trasparenza verso l\'utente, escalation umana nei casi delicati.','Tratamiento de datos conforme al RGPD, transparencia hacia el usuario, escalada humana en los casos delicados.')),
    ]
    ih = ''.join(f'<div class="card rv">{ic(i)}<h3>{a}</h3><p>{b}</p></div>' for i, a, b in items)
    body = f'''
<section class="page-hero solo"><div class="wrap"><div>
  <span class="eyebrow">{t('Tecnologia e sicurezza','Tecnología y seguridad')}</span>
  <h1>{t('Un\'unica piattaforma proprietaria, <span class="grad">oltre 18 mesi di lavoro.</span>','Una única plataforma propia, <span class="grad">más de 18 meses de trabajo.</span>')}</h1>
  <p class="lead">{t('Tutti i prodotti Odyra girano sulla stessa infrastruttura: è la base che permette al gruppo di lanciare nuovi prodotti e nuovi verticali senza ripartire da zero.','Todos los productos de Odyra funcionan sobre la misma infraestructura: es la base que permite al grupo lanzar nuevos productos y verticales sin partir de cero.')}</p>
</div></div></section>
<section><div class="wrap"><div class="grid g3">{ih}</div></div></section>
<section class="alt" id="whatsapp"><div class="wrap grid g2" style="gap:56px;align-items:center">
  <div class="rv"><span class="eyebrow">WhatsApp Business</span><h2>{t('Numeri, template e conversazioni, gestiti dalla piattaforma.','Números, plantillas y conversaciones, gestionados por la plataforma.')}</h2>
    <p class="lead">{t('Odyra è Tech Provider Meta tramite Vonage. Attiviamo i numeri, gestiamo template e conversazioni; la titolarità dell\'account resta al cliente.','Odyra es Tech Provider de Meta a través de Vonage. Activamos los números, gestionamos plantillas y conversaciones; la titularidad de la cuenta sigue siendo del cliente.')}</p></div>
  <div class="card rv"><div style="display:flex;gap:30px;align-items:center;flex-wrap:wrap"><img src="/assets/logos/whatsapp.svg" alt="WhatsApp" style="height:54px"><img src="/assets/logos/meta.svg" alt="Meta" style="height:34px"><img src="/assets/logos/vonage.svg" alt="Vonage" style="height:34px"></div>
    <p style="margin-top:20px;font-size:.9rem;color:var(--muted)">{t('WhatsApp e Meta sono marchi di Meta Platforms, Inc.; Vonage è un marchio di Vonage Holdings Corp. Odyra non è affiliata a tali società.','WhatsApp y Meta son marcas de Meta Platforms, Inc.; Vonage es una marca de Vonage Holdings Corp. Odyra no está afiliada a dichas empresas.')}</p></div>
</div></section>
<section id="conformita"><div class="wrap">
  <div class="sec-h"><span class="eyebrow">{t('Conformità','Cumplimiento')}</span><h2>{t('AI Act e GDPR, dal primo giorno.','AI Act y RGPD, desde el primer día.')}</h2><p class="lead">{t('Per i partner in settori regolati: progettazione nel perimetro di AI Act e GDPR, accordi su dati e cybersecurity, supporto alla documentazione.','Para socios en sectores regulados: diseño dentro del perímetro del AI Act y el RGPD, acuerdos sobre datos y ciberseguridad, apoyo a la documentación.')}</p></div>
  <table>
    <tr><th>{t('Trasparenza','Transparencia')}</th><td>{t('L\'utente sa di parlare con un agente AI.','El usuario sabe que habla con un agente de IA.')}</td></tr>
    <tr><th>{t('Escalation umana','Escalada humana')}</th><td>{t('Nei casi delicati la conversazione passa a una persona.','En los casos delicados la conversación pasa a una persona.')}</td></tr>
    <tr><th>{t('Isolamento dei dati','Aislamiento de datos')}</th><td>{t('Dati e configurazione separati per ogni azienda.','Datos y configuración separados para cada empresa.')}</td></tr>
    <tr><th>{t('Registrazioni e report','Grabaciones e informes')}</th><td>{t('Consultabili dal titolare nella dashboard.','Consultables por el titular en el panel.')}</td></tr>
    <tr><th>{t('Documentazione','Documentación')}</th><td>{t('Supporto ai partner per la documentazione richiesta.','Apoyo a los socios en la documentación requerida.')}</td></tr>
  </table>
</div></section>
{cta(t('Domande su sicurezza e conformità?','¿Preguntas sobre seguridad y cumplimiento?'), t('Il nostro team risponde ai tuoi referenti IT e legali.','Nuestro equipo atiende a tus responsables de TI y legal.'))}'''
    return layout('tecnologia', t('Tecnologia e sicurezza — Odyra System', 'Tecnología y seguridad — Odyra System'), t('Piattaforma multi-tenant, voce in tempo reale, WhatsApp Business come Tech Provider Meta, privacy e AI Act by design.', 'Plataforma multi-tenant, voz en tiempo real, WhatsApp Business como Tech Provider de Meta, privacidad y AI Act desde el diseño.'), body)

# ───────────────────────── CONTATTI ─────────────────────────
def page_contatti():
    opts = [('voce', t('Agenti AI vocali e WhatsApp','Agentes IA de voz y WhatsApp')), ('commerciale', t('Agente commerciale AI','Agente comercial IA')), ('hako', 'HAKO'), ('software-house', t('Partnership per software house','Alianza para software houses')), ('enterprise', 'Enterprise'), ('altro', t('Altro','Otro'))]
    oh = ''.join(f'<option value="{v}">{e(n)}</option>' for v, n in opts)
    body = f'''
<section class="page-hero solo"><div class="wrap"><div>
  <span class="eyebrow">{t('Contatti','Contacto')}</span>
  <h1>{t('Parliamo del tuo caso.','Hablemos de tu caso.')}</h1>
  <p class="lead">{t('Raccontaci come lavori oggi. Ti rispondiamo entro un giorno lavorativo.','Cuéntanos cómo trabajas hoy. Te respondemos en un día laborable.')}</p>
</div></div></section>
<section><div class="wrap grid g2" style="gap:56px;align-items:start;grid-template-columns:1.2fr .8fr">
  <form class="form rv" id="form-contatti" novalidate>
    <div class="row"><label>{t('Nome e cognome','Nombre y apellidos')}<input name="nome" required autocomplete="name"></label><label>{t('Azienda','Empresa')}<input name="azienda" required autocomplete="organization"></label></div>
    <div class="row"><label>E-mail<input type="email" name="email" required autocomplete="email"></label><label>{t('Telefono','Teléfono')}<input type="tel" name="telefono" autocomplete="tel"></label></div>
    <label>{t('Di cosa hai bisogno?','¿Qué necesitas?')}<select name="interesse" required>{oh}</select></label>
    <label>{t('Messaggio','Mensaje')}<textarea name="messaggio" placeholder="{t('Quante chiamate o lead gestite? Che gestionale o CRM usate?','¿Cuántas llamadas o leads gestionáis? ¿Qué software o CRM usáis?')}"></textarea></label>
    <input class="hp" name="company_site" tabindex="-1" autocomplete="off" aria-hidden="true">
    <label class="chk"><input type="checkbox" name="privacy" value="si" required><span>{t('Ho letto l\'<a href="/privacy.html" style="text-decoration:underline">informativa privacy</a> e acconsento al trattamento dei dati per essere ricontattato.','He leído la <a href="/es/privacy.html" style="text-decoration:underline">política de privacidad</a> y consiento el tratamiento de mis datos para ser contactado.')}</span></label>
    <div><button class="btn btn-p" type="submit">{t('Invia la richiesta','Enviar la solicitud')}</button></div>
    <p class="form-msg" id="form-msg" role="status"></p>
  </form>
  <div class="grid" style="gap:16px">
    <div class="card rv">{ic('mail')}<h3>E-mail</h3><p><a href="mailto:{EMAIL}" style="color:var(--blue-d);font-weight:700">{EMAIL}</a></p></div>
    <div class="card rv">{ic('globe')}<h3>{t('Sede','Sede')}</h3><p>Verypos S.r.l.<br>Viale Papiniano 8<br>20123 Milano (MI)<br>P.IVA 11630390968</p></div>
    <div class="card rv">{ic('book')}<h3>{t('Cerchi HAKO?','¿Buscas HAKO?')}</h3><p>{t('Il sito dedicato è','El sitio dedicado es')} <a href="https://hakocondomini.com" rel="noopener" style="color:var(--blue-d);font-weight:700">hakocondomini.com</a></p></div>
  </div>
</div></section>'''
    return layout('contatti', t('Contatti — Odyra System', 'Contacto — Odyra System'), t('Richiedi una demo o parla con il team Odyra: team@odyrasystemautomation.it, Verypos S.r.l., Milano.', 'Solicita una demo o habla con el equipo de Odyra: team@odyrasystemautomation.it, Verypos S.r.l., Milán.'), body)

# ───────────────────────── PRIVACY / 404 ─────────────────────────
def page_privacy():
    body = f'''
<section class="page-hero solo"><div class="wrap"><div><span class="eyebrow">Privacy</span><h1>{t('Informativa sulla privacy','Política de privacidad')}</h1><p class="lead">{t('Bozza da far rivedere a un legale prima della pubblicazione.','Borrador que debe revisar un abogado antes de su publicación.')}</p></div></div></section>
<section><div class="wrap" style="max-width:820px">
<h3>{t('Titolare del trattamento','Responsable del tratamiento')}</h3><p style="margin:8px 0 28px">Verypos S.r.l., Viale Papiniano 8, 20123 Milano — P.IVA 11630390968 — <a href="mailto:{EMAIL}" style="color:var(--blue-d)">{EMAIL}</a></p>
<h3>{t('Dati raccolti','Datos recogidos')}</h3><p style="margin:8px 0 28px">{t('Attraverso il modulo contatti raccogliamo nome, azienda, e-mail, telefono e il contenuto del messaggio, al solo scopo di rispondere alla tua richiesta. Il sito non usa cookie di profilazione.','A través del formulario de contacto recogemos nombre, empresa, e-mail, teléfono y el contenido del mensaje, con la única finalidad de responder a tu solicitud. El sitio no usa cookies de perfilado.')}</p>
<h3>{t('Font esterni','Fuentes externas')}</h3><p style="margin:8px 0 28px">{t('Il sito carica i caratteri tipografici da Google Fonts, che può ricevere il tuo indirizzo IP.','El sitio carga las fuentes tipográficas desde Google Fonts, que puede recibir tu dirección IP.')}</p>
<h3>{t('I tuoi diritti','Tus derechos')}</h3><p style="margin:8px 0 28px">{t('Puoi chiedere accesso, rettifica, cancellazione e opposizione scrivendo a ','Puedes solicitar acceso, rectificación, supresión y oposición escribiendo a ')}{EMAIL}.</p>
</div></section>'''
    return layout('contatti', t('Privacy — Odyra System','Privacidad — Odyra System'), t('Informativa sulla privacy di Odyra System.','Política de privacidad de Odyra System.'), body).replace(f'<link rel="canonical" href="{SITE}{url("contatti")}">', f'<link rel="canonical" href="{SITE}{"/privacy.html" if L=="it" else "/es/privacy.html"}"><meta name="robots" content="noindex">')

def page_404():
    body = f'''<section class="page-hero solo" style="min-height:60vh;display:grid;align-items:center"><div class="wrap"><div><span class="eyebrow">404</span><h1>{t('Qui nessuno risponde.','Aquí nadie responde.')}</h1><p class="lead">{t('La pagina che cerchi non esiste. Odyra, invece, risponde sempre.','La página que buscas no existe. Odyra, en cambio, responde siempre.')}</p><div style="margin-top:28px"><a class="btn btn-p" href="{url('home')}">{t('Torna alla home','Volver al inicio')}</a></div></div></div></section>'''
    return layout('home', t('Pagina non trovata — Odyra System','Página no encontrada — Odyra System'), t('Pagina non trovata.','Página no encontrada.'), body).replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"')

BUILDERS = {'home': page_home, 'gruppo': page_gruppo, 'voce': page_voce, 'commerciale': page_comm, 'hako': page_hako, 'software-house': page_sh, 'enterprise': page_ent, 'casi': page_casi, 'tecnologia': page_tech, 'contatti': page_contatti}

def write(rel, content):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    global L
    urls = []
    for L in ('it', 'es'):
        pre = '' if L == 'it' else 'es/'
        for slug, f in PAGES:
            write(pre + f, BUILDERS[slug]())
            urls.append(url(slug))
        write(pre + 'privacy.html', page_privacy())
        write(pre + '404.html', page_404())
    today = datetime.date.today().isoformat()
    def alt(u):
        it = u[3:] if u.startswith('/es/') else u
        it = it or '/'
        es = '/es/' + it.lstrip('/') if it != '/' else '/es/'
        return it, es
    sm = ''.join(f'<url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod>' + ''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{SITE}{a}"/>' for l, a in zip(('it', 'es'), alt(u))) + '</url>' for u in urls)
    write('sitemap.xml', f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">{sm}</urlset>\n')
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')

if __name__ == '__main__':
    main()
