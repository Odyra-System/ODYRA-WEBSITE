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

PAGES = [('home', 'index.html'), ('gruppo', 'gruppo.html'), ('voce', 'agenti-ai-vocali-whatsapp.html'),
         ('commerciale', 'agente-commerciale-ai.html'), ('hako', 'hako.html'), ('software-house', 'software-house.html'),
         ('enterprise', 'enterprise.html'), ('casi', 'casi-studio.html'), ('tecnologia', 'tecnologia.html'), ('contatti', 'contatti.html')]
FILE = dict(PAGES)

def url(slug, lang=None):
    lang = lang or L
    f = FILE[slug]
    base = '/' if lang == 'it' else '/es/'
    return base if f == 'index.html' else base + f

# ───────── componenti ─────────
def layout(slug, title, desc, body, noindex=False, canonical=None):
    other = 'es' if L == 'it' else 'it'
    cur = lambda s: ' aria-current="page"' if s == slug else ''
    partner = [('software-house', t('Software house', 'Software houses'), t('AI col tuo marchio dentro il tuo gestionale', 'IA con tu marca dentro tu software')),
               ('enterprise', 'Enterprise', t('Progetti su misura per grandi volumi', 'Proyectos a medida para grandes volúmenes'))]
    sol = [('voce', t('Receptionist AI: voce e WhatsApp', 'Recepcionista IA: voz y WhatsApp'), t('Risponde e prenota nel gestionale', 'Responde y reserva en el software')),
           ('commerciale', t('Agente commerciale AI', 'Agente comercial IA'), t('Ogni lead richiamato in meno di un minuto', 'Cada lead llamado en menos de un minuto'))]
    menu = lambda items: ''.join(f'<a href="{url(s)}"><b>{e(n)}</b><small>{e(d)}</small></a>' for s, n, d in items)
    chev = '<svg width="11" height="11" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
    nav = f'''<nav class="nav" id="nav" aria-label="{t('Principale','Principal')}">
      <div class="dd"><button class="nav-link" aria-haspopup="true" aria-expanded="false">{t('Partner','Socios')} {chev}</button><div class="dd-menu">{menu(partner)}</div></div>
      <div class="dd"><button class="nav-link" aria-haspopup="true" aria-expanded="false">{t('Soluzioni AI','Soluciones IA')} {chev}</button><div class="dd-menu">{menu(sol)}</div></div>
      <a class="nav-link" href="{url('hako')}"{cur('hako')}>HAKO</a>
      <a class="nav-link" href="{url('casi')}"{cur('casi')}>{t('Casi studio','Casos de éxito')}</a>
      <a class="nav-link" href="{url('tecnologia')}"{cur('tecnologia')}>{t('Tecnologia','Tecnología')}</a>
      <a class="nav-link" href="{url('gruppo')}"{cur('gruppo')}>{t('Il gruppo','El grupo')}</a>
      <div class="lang" role="group" aria-label="Lingua"><a href="{url(slug,'it')}" hreflang="it"{' aria-current="true"' if L=='it' else ''}>IT</a><a href="{url(slug,'es')}" hreflang="es"{' aria-current="true"' if L=='es' else ''}>ES</a></div>
      <a class="btn btn-p btn-sm" href="{url('contatti')}">{t('Parla con noi','Habla con nosotros')}</a>
    </nav>'''
    path = canonical or url(slug)
    alt = ''.join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{url(slug, l)}">' for l in ('it', 'es')) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{url(slug, "it")}">'
    robots = '<meta name="robots" content="noindex">' if noindex else ''
    return f'''<!doctype html>
<html lang="{L}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{robots}<link rel="canonical" href="{SITE}{path}">
{alt}
<meta property="og:type" content="website"><meta property="og:site_name" content="Odyra System">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE}{path}"><meta property="og:image" content="{SITE}/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#061B3A">
<link rel="icon" href="/assets/icon-192.png" type="image/png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/styles.css?v=3">
</head>
<body>
<a class="skip" href="#main">{t('Vai al contenuto','Ir al contenido')}</a>
<header class="hdr" id="top"><div class="wrap">
  <a class="brand" href="{url('home')}" aria-label="Odyra System"><img src="/assets/logos/odyra.png" alt="Odyra System" width="175" height="42"></a>
  {nav}
  <button class="burger" id="burger" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
</div></header>
<main id="main">
{body}
</main>
{footer()}
<script src="/script.js?v=3" defer></script>
</body>
</html>
'''

def footer():
    pv = '/privacy.html' if L == 'it' else '/es/privacy.html'
    return f'''<footer class="ftr"><div class="wrap">
  <div class="top">
    <div><img class="flogo" src="/assets/logos/odyra-white.png" alt="Odyra System">
      <p>{t('Partner white-label per software house e gruppo di software AI proprietari. Milano.','Socio white-label para software houses y grupo de software de IA propio. Milán.')}</p>
      <div class="partners"><img src="/assets/logos/whatsapp.svg" alt="WhatsApp"><img src="/assets/logos/meta.svg" alt="Meta"><img src="/assets/logos/vonage.svg" alt="Vonage"></div></div>
    <div><h4>{t('Soluzioni','Soluciones')}</h4><ul>
      <li><a href="{url('voce')}">{t('Receptionist AI','Recepcionista IA')}</a></li>
      <li><a href="{url('commerciale')}">{t('Agente commerciale AI','Agente comercial IA')}</a></li>
      <li><a href="{url('hako')}">HAKO</a></li></ul></div>
    <div><h4>{t('Azienda','Empresa')}</h4><ul>
      <li><a href="{url('software-house')}">{t('Per le software house','Para software houses')}</a></li>
      <li><a href="{url('enterprise')}">Enterprise</a></li>
      <li><a href="{url('casi')}">{t('Casi studio','Casos de éxito')}</a></li>
      <li><a href="{url('tecnologia')}">{t('Tecnologia','Tecnología')}</a></li>
      <li><a href="{url('gruppo')}">{t('Il gruppo','El grupo')}</a></li></ul></div>
    <div><h4>{t('Contatti','Contacto')}</h4><ul>
      <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
      <li>Verypos S.r.l.<br>Viale Papiniano 8, 20123 Milano</li>
      <li><a href="{url('contatti')}">{t('Scrivici dal modulo','Escríbenos desde el formulario')}</a></li></ul></div>
  </div>
  <div class="bot"><span>© {datetime.date.today().year} Odyra System · Verypos S.r.l. · P.IVA 11630390968 · REA MI-2615892</span>
  <span><a href="{pv}">Privacy</a> · {t('WhatsApp e Meta sono marchi dei rispettivi proprietari.','WhatsApp y Meta son marcas de sus respectivos propietarios.')}</span></div>
</div></footer>'''

def head_(kicker, h1, lead, btns='', extra=''):
    return f'''<section class="page-head"><div class="wrap"><div><span class="kicker">{kicker}</span><h1>{h1}</h1></div><div><p class="lead">{lead}</p>{('<div class="row-btn">'+btns+'</div>') if btns else ''}{extra}</div></div></section>'''

def sec(inner, cls=''):
    return f'<section class="sec {cls}"><div class="wrap">{inner}</div></section>'

def sec_head(h2, lead=''):
    return f'<div class="sec-head"><h2>{h2}</h2>{f"<p class=lead>{lead}</p>" if lead else "<div></div>"}</div>'

def rows(items):
    out = ''
    for it in items:
        title, text = it[0], it[1]
        href = it[2] if len(it) > 2 else None
        tag = it[3] if len(it) > 3 else ''
        tg = f'<span class="tag">{tag}</span>' if tag else ''
        if href:
            out += f'<a href="{href}"><h3>{title}{tg}</h3><p>{text}</p></a>'
        else:
            out += f'<div><h3>{title}{tg}</h3><p>{text}</p></div>'
    return f'<div class="rows">{out}</div>'

def steps(items, cls=''):
    return f'<ol class="steps {cls}">' + ''.join(f'<li><h3>{a}</h3><p>{b}</p></li>' for a, b in items) + '</ol>'

def cta(h2=None, p=None, interesse='', btn=None):
    h2 = h2 or t('Parliamo del tuo gestionale.', 'Hablemos de tu software.')
    p = p or t('Ti mostriamo come funziona la partnership, con tempi e formula commerciale.', 'Te mostramos cómo funciona la alianza, con plazos y fórmula comercial.')
    q = f'?interesse={interesse}' if interesse else ''
    btn = btn or t('Richiedi una demo', 'Solicita una demo')
    return f'''<section class="sec-ink cta-sec"><div class="wrap"><div><h2>{h2}</h2><p>{p}</p></div><div class="row-btn"><a class="btn btn-w" href="{url('contatti')}{q}">{btn}</a><a class="btn btn-ow" href="mailto:{EMAIL}">{EMAIL}</a></div></div></section>'''

def sportit(lg=False):
    return f'<span class="tile{" tile-lg" if lg else ""}"><img src="/assets/logos/sportit.png" alt="Sportit.com"></span>'

def boss_chip():
    return '<span class="boss-chip"><img src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers"><span>BOSS · GoWeb · GoAgent</span></span>'

def video_slot(name):
    return f'<div class="media" hidden data-video="/assets/video/{name}.mp4"><video controls playsinline preload="metadata" poster="/assets/video/{name}.jpg"></video></div>'

def audio_slot():
    return f'''<section id="audio-demo" class="sec sec-mist" hidden><div class="wrap">{sec_head(t('Chiamate reali dell\'agente.','Llamadas reales del agente.'), t('Registrazioni autentiche, nessuna simulazione.','Grabaciones auténticas, sin simulaciones.'))}<div class="audio-list"></div></div></section>'''

def app_demo(tabs=True):
    tb = f'''<div class="demo-tabs" role="group" aria-label="{t('Marchio del gestionale','Marca del software')}"><button data-skin="boss" aria-pressed="true">{t('Con il marchio BOSS','Con la marca BOSS')}</button><button data-skin="partner" aria-pressed="false">{t('Con il tuo marchio','Con tu marca')}</button></div>''' if tabs else ''
    return f'''<div>{tb}
<div class="app" id="demo" data-skin="boss" data-slot-empty="{t('Il tuo logo','Tu logo')}" role="img" aria-label="{t('Dimostrazione: un agente AI risponde a una chiamata e scrive la prenotazione nell\'agenda del gestionale','Demostración: un agente IA responde a una llamada y escribe la reserva en la agenda del software')}">
  <div class="app-bar"><span class="dots"><i></i><i></i><i></i></span><span class="app-url">{t('gestionale','software') } / {t('agenda','agenda')}</span></div>
  <div class="app-body">
    <aside class="app-side"><div class="slot"></div><nav><span class="on">{t('Agenda','Agenda')}</span><span>{t('Clienti','Clientes')}</span><span>{t('Servizi','Servicios')}</span><span>{t('Agente AI','Agente IA')}</span></nav></aside>
    <section class="app-main"><h4>{t('Venerdì','Viernes')}</h4>
      <ul class="agenda">
        <li><time>09:00</time><b>Marta B.</b><span>{t('Colore','Color')}</span></li>
        <li><time>10:30</time><b>Luca F.</b><span>{t('Taglio','Corte')}</span></li>
        <li class="free"><time>12:00</time><span>{t('Libero','Libre')}</span><span></span></li>
        <li class="new"><time>15:30</time><b>Elena R.</b><span>{t('Taglio e piega','Corte y peinado')}</span><em>{t('Prenotato dall\'agente AI','Reservado por el agente IA')}</em></li>
      </ul></section>
    <section class="app-call"><div class="call-top"><span class="live">{t('In chiamata','En llamada')}</span><span>21:47</span></div>
      <div class="l ai">{t('Buonasera, Salone Aurora. Come posso aiutarla?','Buenas noches, Salón Aurora. ¿En qué puedo ayudarle?')}</div>
      <div class="l cl">{t('Vorrei un taglio e piega venerdì pomeriggio.','Quisiera un corte y peinado el viernes por la tarde.')}</div>
      <div class="l ai">{t('Venerdì alle 15:30 con Giulia è libero. Prenoto?','El viernes a las 15:30 con Giulia está libre. ¿Reservo?')}</div>
      <div class="l cl">{t('Sì, grazie.','Sí, gracias.')}</div>
      <div class="wa-chip"><img src="/assets/logos/whatsapp.svg" alt="WhatsApp"><span>{t('Conferma inviata su WhatsApp','Confirmación enviada por WhatsApp')}</span></div></section>
  </div>
</div>
<p class="demo-cap">{t('Stesso agente, marchio diverso. La conversazione è un esempio; BOSS e GoAgent sono un caso reale.','Mismo agente, marca distinta. La conversación es un ejemplo; BOSS y GoAgent son un caso real.')}</p></div>'''

# ───────── HOME ─────────
def page_home():
    body = f'''
<section class="hero"><div class="wrap">
  <div>
    <h1>{t('Il tuo gestionale, ora risponde.','Tu software, ahora responde.')}</h1>
    <p class="lead">{t('Odyra porta agenti AI vocali e WhatsApp dentro i software di gestione, con il marchio del partner. Tu porti i clienti. Noi portiamo tecnologia, integrazione e gestione.','Odyra lleva agentes IA de voz y WhatsApp a los software de gestión, con la marca del socio. Tú aportas los clientes. Nosotros aportamos tecnología, integración y gestión.')}</p>
    <div class="row-btn"><a class="btn btn-p" href="{url('software-house')}">{t('Diventa partner','Hazte socio')}</a><a class="btn btn-o" href="{url('casi')}#boss">{t('Guarda un caso reale','Mira un caso real')}</a></div>
  </div>
  {app_demo()}
</div></section>

<div class="proof"><div class="wrap"><p>{t('In produzione con','En producción con')}</p>
  <div class="proof-logos">{boss_chip()}{sportit()}<img class="hako-mark" src="/assets/logos/hako.png" alt="HAKO"></div></div></div>

<section class="sec" id="come-funziona"><div class="wrap">
  {sec_head(t('Dal tuo gestionale al ricavo ricorrente, in quattro passi.','De tu software al ingreso recurrente, en cuatro pasos.'), t('Il partner non costruisce nulla. Odyra mette la piattaforma e il lavoro operativo; il servizio esce col nome del partner.','El socio no construye nada. Odyra pone la plataforma y el trabajo operativo; el servicio sale con el nombre del socio.'))}
  {steps([
    (t('Colleghiamo il tuo gestionale','Conectamos tu software'), t('Un connettore dedicato legge servizi, operatori e disponibilità, senza toccare il cuore del tuo software.','Un conector dedicado lee servicios, operarios y disponibilidad, sin tocar el núcleo de tu software.')),
    (t('Attiviamo i tuoi clienti','Activamos a tus clientes'), t('Onboarding automatico a partire dal gestionale. L\'attività mantiene il suo numero di telefono.','Onboarding automático a partir del software. El negocio mantiene su número de teléfono.')),
    (t('L\'agente lavora col tuo marchio','El agente trabaja con tu marca'), t('Risponde al telefono e su WhatsApp e prenota nel tuo software. Ogni schermata porta il tuo logo.','Responde al teléfono y por WhatsApp y reserva en tu software. Cada pantalla lleva tu logo.')),
    (t('Incassi ogni mese','Cobras cada mes'), t('Il servizio è in abbonamento. Condivisione dei ricavi o licenza a volume, con la piattaforma di gestione già pronta.','El servicio es por suscripción. Reparto de ingresos o licencia por volumen, con la plataforma de gestión ya lista.')),
  ])}
</div></section>

<section class="sec sec-mist"><div class="wrap">
  {sec_head(t('Cosa offre il tuo gestionale ai clienti.','Lo que tu software ofrece a los clientes.'), t('Un solo agente per telefono e WhatsApp, più i moduli che si aggiungono sulla stessa piattaforma.','Un solo agente para teléfono y WhatsApp, más los módulos que se suman sobre la misma plataforma.'))}
  {rows([
    (t('Receptionist AI','Recepcionista IA'), t('Risponde a ogni chiamata e messaggio, 24 ore su 24. Prenota, sposta e cancella appuntamenti leggendo servizi, operatori e turni.','Responde a cada llamada y mensaje, las 24 horas. Reserva, mueve y cancela citas leyendo servicios, operarios y turnos.'), url('voce')),
    (t('Agente commerciale','Agente comercial'), t('Richiama ogni nuovo lead in meno di un minuto, lo qualifica e fissa l\'appuntamento nel calendario del team vendite.','Llama a cada nuevo lead en menos de un minuto, lo califica y fija la cita en el calendario del equipo de ventas.'), url('commerciale')),
    (t('Dashboard per i titolari','Panel para los titulares'), t('Chiamate, prenotazioni, report e registrazioni in un solo posto, con il marchio del partner.','Llamadas, reservas, informes y grabaciones en un solo lugar, con la marca del socio.')),
    (t('Customer service e-mail','Atención al cliente por e-mail'), t('Automazione dell\'assistenza, come per i marketplace di Global Trading.','Automatización de la atención, como en los marketplaces de Global Trading.'), url('enterprise')),
    ('Retention AI', t('Richiama i clienti che non tornano da tempo, al telefono o su WhatsApp, e li riporta in agenda.','Vuelve a llamar a los clientes que no regresan desde hace tiempo, por teléfono o WhatsApp, y los devuelve a la agenda.'), None, t('In arrivo','Próximamente')),
  ])}
</div></section>

<section class="sec sec-ink" id="boss"><div class="wrap">
  <div class="case-logo"><img src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers"><span>BOSS · GoWeb · GoAgent</span></div>
  <p class="case-big">{t('BOSS ha aggiunto l\'AI al suo gestionale. Il primo salone ha gestito 262 chiamate in 15 giorni.','BOSS ha añadido la IA a su software. El primer salón gestionó 262 llamadas en 15 días.')}</p>
  <div class="facts">
    <div><b>~1.500</b><span>{t('saloni nella rete GoWeb, a cui BOSS offre GoAgent','salones en la red GoWeb, a los que BOSS ofrece GoAgent')}</span></div>
    <div><b>{t('giugno 2026','junio de 2026')}</b><span>{t('in produzione col marchio BOSS','en producción con la marca BOSS')}</span></div>
    <div><b>24/7</b><span>{t('telefono e WhatsApp, prenotazioni dirette in agenda','teléfono y WhatsApp, reservas directas en la agenda')}</span></div>
  </div>
  <div class="row-btn"><a class="btn btn-w" href="{url('casi')}#boss">{t('Leggi il caso studio','Lee el caso de éxito')}</a></div>
</div></section>

<section class="sec" id="software-gruppo"><div class="wrap split">
  <div>
    <img class="hako-logo" src="/assets/logos/hako.png" alt="HAKO">
    <h2>{t('Odyra costruisce anche software suo.','Odyra también construye software propio.')}</h2>
    <p class="lead" style="margin-top:22px">{t('HAKO è il programma della portineria che sostituisce il quaderno dei pacchi: il portinaio fotografa il pacco, il condomino riceve l\'avviso su WhatsApp, SMS o e-mail nella sua lingua, il ritiro si chiude con un codice.','HAKO es el programa de la conserjería que sustituye al cuaderno de paquetes: el conserje fotografía el paquete, el vecino recibe el aviso por WhatsApp, SMS o e-mail en su idioma, la recogida se cierra con un código.')}</p>
    <p style="margin-top:18px">{t('Nasce sulla stessa piattaforma dei prodotti per i partner. Ogni nuovo verticale parte più veloce del precedente.','Nace sobre la misma plataforma que los productos para socios. Cada nuevo vertical arranca más rápido que el anterior.')}</p>
    <div class="row-btn"><a class="btn btn-o" href="{url('hako')}">{t('Scopri HAKO','Descubre HAKO')}</a></div>
  </div>
  <div class="hako-fig"><img src="/assets/hako-phone.jpg" alt="{t('HAKO legge l\'etichetta del pacco dalla fotocamera','HAKO lee la etiqueta del paquete con la cámara')}" width="310" height="580"></div>
</div></section>

<section class="sec sec-mist"><div class="wrap split">
  <div>{sportit(True)}
    <h2 style="margin-top:34px">{t('Anche le aziende grandi chiedono più velocità.','Las empresas grandes también piden más velocidad.')}</h2></div>
  <div>
    <p class="lead">{t('Global Trading, il gruppo dietro Sportit.com, genera centinaia di lead a campagna. L\'agente commerciale di Odyra scrive su WhatsApp subito, richiama in pochi secondi, qualifica e fissa l\'appuntamento. Capacità da 10 a 1.000 chiamate allo stesso costo.','Global Trading, el grupo detrás de Sportit.com, genera cientos de leads por campaña. El agente comercial de Odyra escribe por WhatsApp al instante, llama en pocos segundos, califica y fija la cita. Capacidad de 10 a 1.000 llamadas al mismo coste.')}</p>
    <div class="row-btn"><a class="btn btn-o" href="{url('casi')}#global-trading">{t('Leggi il caso studio','Lee el caso de éxito')}</a><a class="btn btn-o" href="{url('enterprise')}">Enterprise</a></div>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  {sec_head(t('Affidabile per i settori regolati.','Fiable para los sectores regulados.'), t('Voce e dati girano su infrastruttura dedicata. Per WhatsApp Business, Odyra è Tech Provider Meta tramite Vonage.','Voz y datos funcionan en infraestructura dedicada. Para WhatsApp Business, Odyra es Tech Provider de Meta a través de Vonage.'))}
  {rows([
    (t('Dati isolati per ogni azienda','Datos aislados por cada empresa'), t('Ogni attività ha il proprio agente, i propri dati e la propria configurazione sulla stessa piattaforma.','Cada negocio tiene su propio agente, sus propios datos y su propia configuración sobre la misma plataforma.')),
    (t('GDPR e AI Act fin dal progetto','RGPD y AI Act desde el diseño'), t('Trasparenza verso l\'utente, passaggio a una persona nei casi delicati, supporto alla documentazione per i partner.','Transparencia hacia el usuario, paso a una persona en los casos delicados, apoyo a la documentación para los socios.'), url('tecnologia')+'#conformita'),
    (t('WhatsApp Business ufficiale','WhatsApp Business oficial'), t('Numeri, template e conversazioni gestiti da Odyra. La titolarità dell\'account resta al cliente.','Números, plantillas y conversaciones gestionados por Odyra. La titularidad de la cuenta sigue siendo del cliente.'), url('tecnologia')+'#whatsapp'),
  ])}
</div></section>

{cta()}
'''
    return layout('home', t('Odyra System — AI white-label per gestionali e software proprietari', 'Odyra System — IA white-label para software de gestión y software propio'),
        t('Odyra porta agenti AI vocali e WhatsApp nei gestionali, col marchio del partner, e sviluppa software proprietari come HAKO.', 'Odyra lleva agentes IA de voz y WhatsApp a los software de gestión, con la marca del socio, y desarrolla software propio como HAKO.'), body)

# ───────── GRUPPO ─────────
def page_gruppo():
    body = head_(t('Il gruppo','El grupo'), t('Software AI proprietari. Una sola piattaforma.','Software de IA propio. Una sola plataforma.'),
        t('Odyra è un gruppo tecnologico milanese che sviluppa e possiede software di intelligenza artificiale. Li porta ai clienti in due modi: con il marchio dei partner, o con il proprio.','Odyra es un grupo tecnológico milanés que desarrolla y posee software de inteligencia artificial. Lo lleva a los clientes de dos maneras: con la marca de los socios, o con la propia.'))
    body += sec(f'''{sec_head(t('Missione e visione.','Misión y visión.'))}{rows([
      (t('Missione','Misión'), t('Dare a ogni azienda, dal singolo salone al gruppo industriale, una forza di lavoro AI affidabile, integrata e misurabile.','Dar a cada empresa, del salón individual al grupo industrial, una fuerza de trabajo de IA fiable, integrada y medible.')),
      (t('Visione','Visión'), t('Diventare il gruppo europeo di riferimento per i software AI verticali: prodotti proprietari, ciascuno leader nel proprio mercato, su un\'unica infrastruttura condivisa.','Convertirnos en el grupo europeo de referencia del software de IA vertical: productos propios, cada uno líder en su mercado, sobre una única infraestructura compartida.')),
      (t('Metodo','Método'), t('Risultati, non architetture: chiamate gestite, prenotazioni, tempi di risposta.','Resultados, no arquitecturas: llamadas gestionadas, reservas, tiempos de respuesta.')),
    ])}''')
    body += sec(f'''{sec_head(t('Il portafoglio.','La cartera.'), t('Ogni prodotto ha la propria identità e il proprio mercato. Tutti condividono la stessa piattaforma, sviluppata in oltre 18 mesi.','Cada producto tiene su propia identidad y su propio mercado. Todos comparten la misma plataforma, desarrollada en más de 18 meses.'))}{rows([
      (t('Agenti AI per i partner','Agentes IA para socios'), t('Receptionist AI su voce e WhatsApp e agente commerciale, in white-label per i gestionali. Caso reale: BOSS e GoAgent.','Recepcionista IA por voz y WhatsApp y agente comercial, en white-label para software de gestión. Caso real: BOSS y GoAgent.'), url('software-house')),
      ('HAKO', t('Gestione pacchi per condomini con portineria. Prodotto proprietario di Odyra.','Gestión de paquetes para comunidades con conserjería. Producto propio de Odyra.'), url('hako')),
      (t('Progetti enterprise','Proyectos enterprise'), t('Agenti e automazioni su misura per aziende con grandi volumi.','Agentes y automatizaciones a medida para empresas con grandes volúmenes.'), url('enterprise')),
      (t('Nuovi verticali','Nuevos verticales'), t('In sviluppo sulla stessa infrastruttura, in Italia e in Spagna.','En desarrollo sobre la misma infraestructura, en Italia y en España.'), None, t('In arrivo','Próximamente')),
    ])}''', 'sec-mist')
    body += sec(f'''<table><tr><th>{t('Società','Sociedad')}</th><td>Verypos S.r.l.</td></tr><tr><th>{t('Sede','Sede')}</th><td>Viale Papiniano 8, 20123 Milano</td></tr><tr><th>{t('Mercati','Mercados')}</th><td>{t('Italia e Spagna','Italia y España')}</td></tr><tr><th>{t('Contatto','Contacto')}</th><td><a class="link" href="mailto:{EMAIL}">{EMAIL}</a></td></tr></table>''')
    body += cta(t('Lavoriamo insieme.','Trabajemos juntos.'), t('Che tu sia una software house o un\'azienda, raccontaci il tuo caso.','Seas una software house o una empresa, cuéntanos tu caso.'))
    return layout('gruppo', t('Il gruppo — Odyra System', 'El grupo — Odyra System'), t('Missione, visione e portafoglio di Odyra: partner white-label e software AI proprietari, da Milano.', 'Misión, visión y cartera de Odyra: socio white-label y software de IA propio, desde Milán.'), body)

# ───────── VOCE ─────────
def page_voce():
    body = head_(t('Soluzione AI','Solución IA'), t('Una receptionist che non stacca mai.','Una recepcionista que nunca desconecta.'),
        t('Risponde a ogni chiamata e a ogni messaggio WhatsApp, giorno e notte, e prenota direttamente nel gestionale. Odyra la offre ai software house con il loro marchio.','Responde a cada llamada y a cada mensaje de WhatsApp, de día y de noche, y reserva directamente en el software. Odyra la ofrece a las software houses con su marca.'),
        f'<a class="btn btn-p" href="{url("contatti")}?interesse=voce">{t("Richiedi una demo","Solicita una demo")}</a><a class="btn btn-o" href="{url("software-house")}">{t("Per le software house","Para software houses")}</a>')
    body += sec('<div style="max-width:940px">' + app_demo(False) + '</div>', 'sec-mist')
    body += sec(f'''{sec_head(t('Cosa fa.','Qué hace.'))}{rows([
      (t('Risponde','Responde'), t('Al telefono con voce naturale in italiano e su WhatsApp, 24/7, anche su più conversazioni in contemporanea.','Al teléfono con voz natural y por WhatsApp, 24/7, incluso en varias conversaciones a la vez.')),
      (t('Prenota','Reserva'), t('Prenota, sposta e cancella appuntamenti in tempo reale, leggendo servizi, operatori, turni e disponibilità.','Reserva, mueve y cancela citas en tiempo real, leyendo servicios, operarios, turnos y disponibilidad.')),
      (t('Conferma e ricorda','Confirma y recuerda'), t('Notifiche WhatsApp automatiche per confermare e ricordare ogni appuntamento.','Notificaciones automáticas de WhatsApp para confirmar y recordar cada cita.')),
      (t('Informa','Informa'), t('Risponde su servizi, prezzi e orari a partire dalla base di conoscenza dell\'attività.','Responde sobre servicios, precios y horarios a partir de la base de conocimiento del negocio.')),
      (t('Passa la mano','Cede el paso'), t('Quando serve, passa la conversazione a una persona del team.','Cuando hace falta, pasa la conversación a una persona del equipo.')),
      (t('Rende conto','Rinde cuentas'), t('Il titolare vede tutto in una dashboard: chiamate, prenotazioni, report, registrazioni.','El titular lo ve todo en un panel: llamadas, reservas, informes, grabaciones.')),
    ])}''')
    body += audio_slot()
    body += sec(f'''{sec_head(t('Quello che cambia per l\'attività.','Lo que cambia para el negocio.'))}{rows([
      (t('Nessuna chiamata persa','Ninguna llamada perdida'), t('Il telefono risponde anche quando lo staff è occupato o il negozio è chiuso.','El teléfono responde aunque el equipo esté ocupado o el local cerrado.')),
      (t('Agenda piena','Agenda llena'), t('Le prenotazioni arrivano a qualsiasi ora, direttamente nel gestionale.','Las reservas llegan a cualquier hora, directamente en el software.')),
      (t('Meno lavoro ripetitivo','Menos trabajo repetitivo'), t('Lo staff smette di rispondere sempre alle stesse domande.','El equipo deja de responder siempre a las mismas preguntas.')),
      (t('Numero invariato','Número sin cambios'), t('L\'attività mantiene il suo numero di telefono.','El negocio mantiene su número de teléfono.')),
      (t('Attivazione rapida','Activación rápida'), t('Onboarding guidato e configurazione automatica a partire dal gestionale.','Onboarding guiado y configuración automática a partir del software.')),
    ])}
    <p style="margin-top:34px">{t('Per saloni, centri estetici, studi dentistici, cliniche veterinarie, centri sportivi e ogni attività che vive di appuntamenti.','Para salones, centros de estética, clínicas dentales, clínicas veterinarias, centros deportivos y cualquier negocio que viva de citas.')}</p>''', 'sec-mist')
    body += sec(f'''<div class="split"><div><div class="boss-chip" style="margin-bottom:28px"><img src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers"><span>BOSS · GoWeb</span></div><h2>{t('GoAgent è il prodotto BOSS, costruito da Odyra.','GoAgent es el producto de BOSS, construido por Odyra.')}</h2></div>
      <div><p class="lead">{t('BOSS offre GoAgent ai saloni della rete GoWeb col proprio marchio. In produzione da giugno 2026, con 262 chiamate gestite nei primi 15 giorni nel salone pilota.','BOSS ofrece GoAgent a los salones de la red GoWeb con su marca. En producción desde junio de 2026, con 262 llamadas gestionadas en los primeros 15 días en el salón piloto.')}</p>
      <div class="row-btn"><a class="btn btn-o" href="{url('casi')}#boss">{t('Leggi il caso studio','Lee el caso de éxito')}</a></div></div></div>''')
    body += sec(f'''<div class="split"><div><span class="tag" style="margin:0 0 16px">{t('In arrivo','Próximamente')}</span><h2>Retention AI</h2></div><div><p class="lead">{t('Il modulo che richiama automaticamente i clienti che non tornano da tempo, al telefono o su WhatsApp, e li riporta in agenda.','El módulo que vuelve a llamar automáticamente a los clientes que no regresan desde hace tiempo, por teléfono o WhatsApp, y los devuelve a la agenda.')}</p></div></div>''', 'sec-mist')
    body += cta(t('Metti la receptionist AI nel tuo gestionale.','Pon la recepcionista IA en tu software.'), None, 'voce')
    return layout('voce', t('Receptionist AI: voce e WhatsApp — Odyra System', 'Recepcionista IA: voz y WhatsApp — Odyra System'), t('La receptionist AI che risponde al telefono e su WhatsApp 24/7 e prenota nel gestionale. In white-label per le software house.', 'La recepcionista IA que responde al teléfono y por WhatsApp 24/7 y reserva en el software. En white-label para software houses.'), body)

# ───────── COMMERCIALE ─────────
def page_comm():
    body = head_(t('Soluzione AI','Solución IA'), t('Chi arriva primo vende.','Quien llega primero vende.'),
        t('L\'agente commerciale richiama ogni nuovo lead in meno di un minuto, lo qualifica al telefono in italiano e fissa l\'appuntamento con il team vendite. Odyra fa arrivare primi sempre.','El agente comercial llama a cada nuevo lead en menos de un minuto, lo califica por teléfono y fija la cita con el equipo de ventas. Odyra hace llegar primero siempre.'),
        f'<a class="btn btn-p" href="{url("contatti")}?interesse=commerciale">{t("Richiedi una demo","Solicita una demo")}</a><a class="btn btn-o" href="{url("casi")}#global-trading">{t("Il caso Global Trading","El caso Global Trading")}</a>')
    body += sec(f'''{sec_head(t('Dal modulo all\'appuntamento, in sei passi.','Del formulario a la cita, en seis pasos.'), t('Nessun lead aspetta. Nessun lead viene dimenticato.','Ningún lead espera. Ningún lead se olvida.'))}{steps([
      (t('Il lead compila un modulo','El lead rellena un formulario'), t('Da campagne Meta, sito o landing page.','Desde campañas de Meta, web o landing page.')),
      (t('Riceve un messaggio WhatsApp','Recibe un mensaje de WhatsApp'), t('Il benvenuto arriva subito, appena il contatto è registrato.','La bienvenida llega al instante, en cuanto se registra el contacto.')),
      (t('Lo chiama l\'agente, entro 60 secondi','Le llama el agente, en menos de 60 segundos'), t('Qualificazione con domande strutturate su bisogno, budget e tempi.','Calificación con preguntas estructuradas sobre necesidad, presupuesto y plazos.')),
      (t('L\'appuntamento va in calendario','La cita va al calendario'), t('Se il lead è in target, finisce nel calendario del commerciale, con conferma su WhatsApp.','Si el lead encaja, va al calendario del comercial, con confirmación por WhatsApp.')),
      (t('Se non risponde, riprova','Si no contesta, reintenta'), t('L\'agente richiama negli orari giusti e lo recupera su WhatsApp.','El agente vuelve a llamar en los horarios adecuados y lo recupera por WhatsApp.')),
      (t('L\'esito va nel CRM','El resultado va al CRM'), t('Ogni esito viene scritto nel CRM dell\'azienda.','Cada resultado se escribe en el CRM de la empresa.')),
    ], 'steps-6')}''')
    body += sec(f'''{sec_head(t('Perché funziona.','Por qué funciona.'))}{rows([
      (t('Da ore a secondi','De horas a segundos'), t('Speed-to-lead 7 giorni su 7, anche di notte e nei festivi.','Speed-to-lead 7 días a la semana, también de noche y festivos.')),
      (t('Da 10 a 1.000 chiamate','De 10 a 1.000 llamadas'), t('La capacità non dipende dall\'organico: nessuna assunzione.','La capacidad no depende de la plantilla: sin contrataciones.')),
      (t('Qualità costante','Calidad constante'), t('Ogni lead riceve la stessa qualificazione, dal primo all\'ultimo.','Cada lead recibe la misma calificación, del primero al último.')),
      (t('Nessun lead perso','Ningún lead perdido'), t('Chi non risponde al telefono rientra da WhatsApp.','Quien no contesta al teléfono vuelve por WhatsApp.')),
      (t('Più valore dalla stessa spesa','Más valor del mismo gasto'), t('I contatti delle campagne vengono lavorati tutti, subito.','Todos los contactos de las campañas se trabajan, de inmediato.')),
    ])}
    <p style="margin-top:34px">{t('Per aziende con campagne di lead generation, reti commerciali, franchising, e-commerce e agenzie di marketing.','Para empresas con campañas de generación de leads, redes comerciales, franquicias, e-commerce y agencias de marketing.')}</p>''', 'sec-mist')
    body += sec(f'''<div class="split"><div>{sportit(True)}<h2 style="margin-top:34px">{t('Dieci chiamate o mille, stesso team.','Diez llamadas o mil, el mismo equipo.')}</h2></div>
      <div><p class="lead">{t('Global Trading, il gruppo dietro Sportit.com, ottiene il primo contatto sotto il minuto e una capacità da 10 a 1.000 chiamate allo stesso costo, indipendente dall\'organico.','Global Trading, el grupo detrás de Sportit.com, consigue el primer contacto en menos de un minuto y una capacidad de 10 a 1.000 llamadas al mismo coste, independiente de la plantilla.')}</p>
      <div class="row-btn"><a class="btn btn-o" href="{url('casi')}#global-trading">{t('Leggi il caso studio','Lee el caso de éxito')}</a></div></div></div>''')
    body += cta(t('Richiama ogni lead prima degli altri.','Llama a cada lead antes que los demás.'), None, 'commerciale')
    return layout('commerciale', t('Agente commerciale AI — Odyra System', 'Agente comercial IA — Odyra System'), t('Richiama ogni nuovo lead in meno di un minuto, lo qualifica al telefono e fissa l\'appuntamento nel calendario del team vendite.', 'Llama a cada nuevo lead en menos de un minuto, lo califica por teléfono y fija la cita en el calendario del equipo de ventas.'), body)

# ───────── HAKO ─────────
def page_hako():
    body = f'''<section class="page-head"><div class="wrap"><div><img class="hako-logo" src="/assets/logos/hako.png" alt="HAKO"><h1>{t('Ogni pacco in portineria, ogni condomino avvisato.','Cada paquete en conserjería, cada vecino avisado.')}</h1></div>
      <div><p class="lead">{t('HAKO registra il pacco con una foto, avvisa il destinatario su WhatsApp, SMS o e-mail nella sua lingua e chiude la consegna con un codice di ritiro.','HAKO registra el paquete con una foto, avisa al destinatario por WhatsApp, SMS o e-mail en su idioma y cierra la entrega con un código de recogida.')}</p>
      <div class="row-btn"><a class="btn btn-p" href="{url('contatti')}?interesse=hako">{t('Richiedi una demo','Solicita una demo')}</a><a class="btn btn-o" href="https://hakocondomini.com" rel="noopener">hakocondomini.com</a></div></div></div></section>'''
    body += sec(f'''<div class="split split-r"><div>{sec_head(t('Tre passaggi, nessun registro cartaceo.','Tres pasos, ningún registro en papel.'))[:0]}<h2>{t('Tre passaggi, nessun registro cartaceo.','Tres pasos, ningún registro en papel.')}</h2><p class="lead" style="margin:22px 0 40px">{t('HAKO sostituisce il quaderno dei pacchi. Il portinaio registra, HAKO avvisa da solo e tiene lo storico di ogni consegna.','HAKO sustituye al cuaderno de paquetes. El conserje registra, HAKO avisa solo y guarda el historial de cada entrega.')}</p>
      {rows([
        (t('Il portinaio fotografa il pacco','El conserje fotografía el paquete'), t('HAKO legge destinatario e corriere dall\'etichetta, oppure scansiona il codice a barre. Il portinaio controlla e conferma.','HAKO lee destinatario y transportista de la etiqueta, o escanea el código de barras. El conserje revisa y confirma.')),
        (t('Il condomino riceve l\'avviso','El vecino recibe el aviso'), t('Un messaggio con corriere, condominio e codice di ritiro, nella lingua che ha scelto.','Un mensaje con transportista, comunidad y código de recogida, en el idioma que ha elegido.')),
        (t('Il ritiro si chiude con il codice','La recogida se cierra con el código'), t('Il condomino mostra il codice, il portinaio registra la consegna e arriva la conferma. Lo storico resta consultabile.','El vecino muestra el código, el conserje registra la entrega y llega la confirmación. El historial queda consultable.')),
      ])}</div>
      <div class="hako-fig"><img src="/assets/hako-phone.jpg" alt="{t('HAKO legge l\'etichetta del pacco','HAKO lee la etiqueta del paquete')}" width="310" height="580"></div></div>''')
    body += sec(f'''{sec_head(t('Come arriva l\'avviso.','Cómo llega el aviso.'), t('HAKO usa i servizi di messaggistica ufficiali. Tu non configuri niente: ci pensiamo noi. Ogni residente sceglie il suo canale.','HAKO usa los servicios de mensajería oficiales. Tú no configuras nada: nos encargamos nosotros. Cada residente elige su canal.'))}
      {rows([
        ('WhatsApp', t('L\'avviso arriva dal numero WhatsApp Business di HAKO, non dal telefono del portinaio, con messaggi approvati in ogni lingua.','El aviso llega desde el número de WhatsApp Business de HAKO, no desde el teléfono del conserje, con mensajes aprobados en cada idioma.')),
        ('SMS', t('Per chi non usa WhatsApp e per la conferma di ritiro. Nessuna app, nessuna connessione dati.','Para quien no usa WhatsApp y para la confirmación de recogida. Sin app ni conexión de datos.')),
        ('E-mail', t('Gli stessi dati, per chi preferisce la posta o non vuole dare il cellulare.','Los mismos datos, para quien prefiere el correo o no quiere dar el móvil.')),
      ])}<div style="display:flex;gap:26px;align-items:center;margin-top:34px"><img src="/assets/logos/whatsapp.svg" alt="WhatsApp" style="height:34px"><img src="/assets/logos/meta.svg" alt="Meta" style="height:26px"></div>''', 'sec-mist')
    body += sec(f'''{sec_head(t('Per chi lavora in portineria, per chi aspetta il pacco, per chi amministra.','Para quien trabaja en conserjería, para quien espera el paquete, para quien administra.'))}
      {rows([
        (t('Il portinaio','El conserje'), t('Lettura dell\'etichetta con la fotocamera. Registra anche senza connessione e sincronizza quando torna la rete. Passaggio di consegne a fine turno.','Lectura de la etiqueta con la cámara. Registra incluso sin conexión y sincroniza al volver la red. Relevo de turno al final de la jornada.')),
        (t('Il condomino','El vecino'), t('Avviso sul canale che preferisce, codice QR di ritiro, delega a un\'altra persona. Accede ai suoi pacchi con un codice via SMS, senza password e senza app.','Aviso por el canal que prefiere, código QR de recogida, delegación en otra persona. Accede a sus paquetes con un código por SMS, sin contraseña ni app.')),
        (t('Chi amministra','Quien administra'), t('Storico completo con foto, orari e nome di chi ha ritirato. Solleciti automatici dopo i giorni che decidi. Residenti importati da CSV o Excel.','Historial completo con fotos, horas y nombre de quien recogió. Recordatorios automáticos tras los días que decidas. Residentes importados desde CSV o Excel.')),
      ])}''')
    body += sec(f'''{sec_head(t('I dati dei residenti restano sotto controllo.','Los datos de los residentes siguen bajo control.'))}
      {rows([
        (t('Cancellazione automatica','Borrado automático'), t('Foto e dati letti dall\'etichetta vengono cancellati dopo un periodo stabilito.','Fotos y datos leídos de la etiqueta se borran tras un periodo establecido.')),
        (t('Esportazione e cancellazione','Exportación y borrado'), t('Ogni residente può chiedere i propri dati o la loro cancellazione, come previsto dal GDPR.','Cada residente puede pedir sus datos o su borrado, como prevé el RGPD.')),
        (t('Registro delle operazioni','Registro de operaciones'), t('Ogni azione resta registrata, con chi l\'ha fatta e quando.','Cada acción queda registrada, con quién la hizo y cuándo.')),
        (t('Accessi per ruolo','Accesos por rol'), t('Portinaio, amministratore e condomino vedono solo ciò che serve al loro lavoro.','Conserje, administrador y vecino ven solo lo que necesitan para su trabajo.')),
      ])}''', 'sec-ink')
    body += sec(f'''{sec_head(t('Domande frequenti.','Preguntas frecuentes.'))}
      {rows([
        (t('Il condomino deve installare un\'app?','¿El vecino debe instalar una app?'), t('No. Riceve l\'avviso sul canale che usa già e, per vedere i suoi pacchi, apre una pagina dal browser del telefono.','No. Recibe el aviso por el canal que ya usa y, para ver sus paquetes, abre una página en el navegador del móvil.')),
        (t('Serve un\'attrezzatura speciale?','¿Hace falta equipo especial?'), t('Basta un tablet o un computer con la fotocamera. HAKO si apre dal browser e funziona anche quando la connessione cade.','Basta una tablet o un ordenador con cámara. HAKO se abre desde el navegador y funciona incluso cuando se cae la conexión.')),
        (t('Come si parte?','¿Cómo se empieza?'), t('Ci mandi l\'elenco dei residenti in CSV o Excel, lo importiamo, creiamo gli accessi e si comincia dai pacchi di oggi.','Nos envías la lista de residentes en CSV o Excel, la importamos, creamos los accesos y se empieza con los paquetes de hoy.')),
        (t('Il condomino può rispondere al messaggio?','¿El vecino puede responder al mensaje?'), t('Per ora l\'avviso è a senso unico: il ritiro si fa mostrando il codice in portineria.','Por ahora el aviso es unidireccional: la recogida se hace mostrando el código en conserjería.')),
        (t('Quanto costa?','¿Cuánto cuesta?'), t('Stiamo aprendo i primi stabili pilota con condizioni dedicate. Scrivici quanti condomini gestisci e ti mandiamo una proposta.','Estamos abriendo los primeros edificios piloto con condiciones dedicadas. Dinos cuántos vecinos gestionas y te enviamos una propuesta.')),
      ])}<p style="margin-top:30px"><a class="link" href="https://hakocondomini.com" rel="noopener">{t('Tutti i dettagli su hakocondomini.com','Todos los detalles en hakocondomini.com')}</a></p>''', 'sec-mist')
    body += cta(t('Prova HAKO nel tuo stabile.','Prueba HAKO en tu edificio.'), t('Stiamo aprendo i primi stabili pilota. Raccontaci come lavorate oggi in portineria.','Estamos abriendo los primeros edificios piloto. Cuéntanos cómo trabajáis hoy en conserjería.'), 'hako')
    return layout('hako', t('HAKO — Gestione pacchi per condomini con portineria', 'HAKO — Gestión de paquetes para comunidades con conserjería'), t('HAKO registra il pacco con una foto e avvisa il condomino su WhatsApp, SMS o e-mail nella sua lingua. Software proprietario di Odyra.', 'HAKO registra el paquete con una foto y avisa al vecino por WhatsApp, SMS o e-mail en su idioma. Software propio de Odyra.'), body)

# ───────── SOFTWARE HOUSE ─────────
def page_sh():
    body = head_(t('Per le software house','Para software houses'), t('Il tuo marchio. La nostra piattaforma.','Tu marca. Nuestra plataforma.'),
        t('Offri ai tuoi clienti un nuovo servizio AI col tuo nome, crea un ricavo ricorrente e non costruire nulla internamente. Il partner porta i clienti; Odyra porta prodotto, tecnologia e gestione operativa.','Ofrece a tus clientes un nuevo servicio de IA con tu nombre, crea un ingreso recurrente y no construyas nada internamente. El socio aporta los clientes; Odyra aporta producto, tecnología y gestión operativa.'),
        f'<a class="btn btn-p" href="{url("contatti")}?interesse=software-house">{t("Diventa partner","Hazte socio")}</a><a class="btn btn-o" href="{url("casi")}#boss">{t("Il caso BOSS","El caso BOSS")}</a>')
    body += sec(app_demo(), 'sec-mist')
    body += sec(f'''{sec_head(t('Cosa include.','Qué incluye.'), t('Tutto quello che serve per lanciare il servizio, già pronto.','Todo lo necesario para lanzar el servicio, ya listo.'))}{rows([
      (t('Integrazione nel tuo gestionale','Integración en tu software'), t('Un connettore dedicato collega il tuo software alla piattaforma, senza toccarne il cuore: più veloce per te, più solido per tutti.','Un conector dedicado conecta tu software con la plataforma, sin tocar su núcleo: más rápido para ti, más sólido para todos.')),
      (t('Agenti AI col tuo marchio','Agentes IA con tu marca'), t('Agenti vocali e WhatsApp, e interfacce sempre col tuo logo.','Agentes de voz y WhatsApp, e interfaces siempre con tu logo.')),
      (t('Onboarding dei clienti','Onboarding de clientes'), t('Attivazione automatica a partire dal gestionale: i tuoi clienti partono in fretta.','Activación automática a partir del software: tus clientes arrancan rápido.')),
      (t('Dashboard per i titolari','Panel para los titulares'), t('Chiamate, prenotazioni, report e registrazioni, già pronti.','Llamadas, reservas, informes y grabaciones, ya listos.')),
      (t('Piattaforma di revenue share','Plataforma de revenue share'), t('Gestione dei ricavi condivisi, senza costruire nulla.','Gestión de los ingresos compartidos, sin construir nada.')),
      (t('WhatsApp Business gestito','WhatsApp Business gestionado'), t('Numeri, template e conversazioni gestiti da Odyra come Tech Provider Meta tramite Vonage. La titolarità dell\'account resta al cliente.','Números, plantillas y conversaciones gestionados por Odyra como Tech Provider de Meta a través de Vonage. La titularidad de la cuenta sigue siendo del cliente.')),
      (t('Conformità','Cumplimiento'), t('Progettazione nel perimetro di AI Act e GDPR e supporto alla documentazione, per i partner in settori regolati.','Diseño dentro del perímetro del AI Act y el RGPD y apoyo a la documentación, para socios en sectores regulados.'), url('tecnologia')+'#conformita'),
    ])}''')
    body += sec(f'''<div class="split"><div><h2>{t('Due formule.','Dos fórmulas.')}</h2></div><div>{rows([
      (t('Condivisione dei ricavi','Reparto de ingresos'), t('Il servizio è in abbonamento: i ricavi si dividono tra te e Odyra, calcolati dalla piattaforma.','El servicio es por suscripción: los ingresos se reparten entre tú y Odyra, calculados por la plataforma.')),
      (t('Licenza a volume','Licencia por volumen'), t('Paghi per volume di utilizzo e stabilisci tu il prezzo ai tuoi clienti.','Pagas por volumen de uso y fijas tú el precio a tus clientes.')),
    ])}</div></div>''', 'sec-mist')
    body += sec(f'''<div class="split"><div><div class="boss-chip" style="margin-bottom:28px"><img src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers"><span>BOSS · GoWeb</span></div><h2>{t('BOSS ha già scelto questa strada.','BOSS ya ha elegido este camino.')}</h2></div>
      <div><p class="lead">{t('Con GoAgent, BOSS ha aggiunto al gestionale GoWeb un servizio AI in abbonamento, pronto per l\'intera rete di circa 1.500 saloni. Odyra ha costruito l\'agente, l\'onboarding automatico, la dashboard e la gestione dei ricavi condivisi.','Con GoAgent, BOSS ha añadido al software GoWeb un servicio de IA por suscripción, listo para toda la red de unos 1.500 salones. Odyra construyó el agente, el onboarding automático, el panel y la gestión de los ingresos compartidos.')}</p>
      <div class="row-btn"><a class="btn btn-o" href="{url('casi')}#boss">{t('Leggi il caso studio','Lee el caso de éxito')}</a></div></div></div>''')
    body += cta(t('Porta l\'AI nel tuo gestionale.','Lleva la IA a tu software.'), t('Parliamo di integrazione, formula commerciale e tempi.','Hablemos de integración, fórmula comercial y plazos.'), 'software-house', t('Diventa partner','Hazte socio'))
    return layout('software-house', t('Per le software house — AI white-label · Odyra System', 'Para software houses — IA white-label · Odyra System'), t('AI white-label per gestionali verticali e SaaS: agenti vocali e WhatsApp col tuo marchio, integrati nel tuo software, con revenue share pronto.', 'IA white-label para software verticales y SaaS: agentes de voz y WhatsApp con tu marca, integrados en tu software, con revenue share listo.'), body)

# ───────── ENTERPRISE ─────────
def page_ent():
    body = head_('Enterprise', t('Agenti AI disegnati sui tuoi processi.','Agentes IA diseñados sobre tus procesos.'),
        t('Per gruppi industriali e aziende con grandi volumi: agenti e automazioni su misura per vendite, customer service e back office, integrati con CRM ed ERP.','Para grupos industriales y empresas con grandes volúmenes: agentes y automatizaciones a medida para ventas, atención al cliente y back office, integrados con CRM y ERP.'),
        f'<a class="btn btn-p" href="{url("contatti")}?interesse=enterprise">{t("Parliamo del progetto","Hablemos del proyecto")}</a>')
    body += sec(f'''{sec_head(t('Dove l\'AI fa lavoro vero.','Donde la IA hace trabajo real.'))}{rows([
      (t('Vendite','Ventas'), t('Qualificazione dei lead, richiami, fissaggio appuntamenti, aggiornamento del CRM.','Calificación de leads, llamadas, fijación de citas, actualización del CRM.'), url('commerciale')),
      ('Customer service', t('Voce, WhatsApp ed e-mail: risposte coerenti, con passaggio a una persona quando serve.','Voz, WhatsApp y e-mail: respuestas coherentes, con paso a una persona cuando hace falta.')),
      ('Back office', t('Automazioni sui processi ripetitivi, tra i sistemi che l\'azienda usa già.','Automatizaciones en procesos repetitivos, entre los sistemas que la empresa ya usa.')),
      (t('Integrazione CRM ed ERP','Integración CRM y ERP'), t('Agenti che leggono e scrivono dove sono i dati.','Agentes que leen y escriben donde están los datos.')),
    ])}''')
    body += sec(f'''{sec_head(t('Dal processo alla produzione, in quattro passi.','Del proceso a la producción, en cuatro pasos.'), t('Lavoriamo su una piattaforma proprietaria già in produzione: i tempi si accorciano e l\'affidabilità non è da dimostrare.','Trabajamos sobre una plataforma propia ya en producción: los plazos se acortan y la fiabilidad no hay que demostrarla.'))}{steps([
      (t('Analisi del processo','Análisis del proceso'), t('Partiamo dai flussi reali: dove si perdono chiamate, tempo e margine.','Partimos de los flujos reales: dónde se pierden llamadas, tiempo y margen.')),
      (t('Disegno dell\'agente','Diseño del agente'), t('Definiamo cosa deve fare, cosa sa e quando passa la mano a una persona.','Definimos qué debe hacer, qué sabe y cuándo cede el paso a una persona.')),
      (t('Integrazione','Integración'), t('Connettiamo CRM, ERP e gestionali con connettori dedicati.','Conectamos CRM, ERP y software de gestión con conectores dedicados.')),
      (t('Produzione e misura','Producción y medición'), t('Dashboard con chiamate, esiti e tempi, per migliorare ogni settimana.','Panel con llamadas, resultados y tiempos, para mejorar cada semana.')),
    ])}''', 'sec-mist')
    body += sec(f'''<div class="split"><div>{sportit(True)}<h2 style="margin-top:34px">{t('Un caso enterprise: dai lead al customer service.','Un caso enterprise: de los leads a la atención al cliente.')}</h2></div>
      <div><p class="lead">{t('Per Global Trading, il gruppo dietro Sportit.com, Odyra ha costruito l\'agente commerciale che richiama ogni lead in meno di un minuto. La collaborazione prosegue con l\'automazione del customer service e-mail per i marketplace.','Para Global Trading, el grupo detrás de Sportit.com, Odyra construyó el agente comercial que llama a cada lead en menos de un minuto. La colaboración continúa con la automatización de la atención por e-mail para marketplaces.')}</p>
      <div class="row-btn"><a class="btn btn-o" href="{url('casi')}#global-trading">{t('Leggi il caso studio','Lee el caso de éxito')}</a></div></div></div>''')
    body += cta(t('Hai un processo da automatizzare?','¿Tienes un proceso que automatizar?'), t('Raccontacelo: ti diciamo cosa si può fare e in quanto tempo.','Cuéntanoslo: te decimos qué se puede hacer y en cuánto tiempo.'), 'enterprise')
    return layout('enterprise', t('Enterprise — Progetti AI su misura · Odyra System', 'Enterprise — Proyectos de IA a medida · Odyra System'), t('Agenti e automazioni AI su misura per vendite, customer service e back office, integrati con CRM ed ERP.', 'Agentes y automatizaciones IA a medida para ventas, atención al cliente y back office, integrados con CRM y ERP.'), body)

# ───────── CASI ─────────
def page_casi():
    body = head_(t('Casi studio','Casos de éxito'), t('Due clienti, due modi di lavorare.','Dos clientes, dos formas de trabajar.'),
        t('Una partnership white-label con un gestionale nazionale e un agente commerciale per un gruppo e-commerce.','Una alianza white-label con un software de gestión nacional y un agente comercial para un grupo de e-commerce.'))
    body += f'''<section class="sec" id="boss"><div class="wrap">
  <div class="case-logo" style="margin-bottom:28px"><img src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers"><span style="color:var(--ink)">BOSS · GoWeb · GoAgent</span></div>
  <h2 style="max-width:22ch">{t('L\'AI dentro il gestionale dei saloni.','La IA dentro el software de los salones.')}</h2>
  <div class="split" style="margin-top:44px"><div><p class="lead">{t('BOSS (Business Orientato ai Servizi per il Salone S.r.l.) sviluppa GoWeb, uno dei gestionali più diffusi tra parrucchieri e centri estetici in Italia, con una rete di circa 1.500 saloni.','BOSS (Business Orientato ai Servizi per il Salone S.r.l.) desarrolla GoWeb, uno de los software de gestión más extendidos entre peluquerías y centros de estética en Italia, con una red de unos 1.500 salones.')}</p></div>
  <div>{rows([
    (t('La sfida','El reto'), t('I saloni perdono prenotazioni ogni giorno: il telefono squilla mentre lo staff lavora, i messaggi arrivano a negozio chiuso. BOSS voleva offrire ai propri clienti un assistente AI vero, integrato nel gestionale, senza costruirlo in casa.','Los salones pierden reservas cada día: el teléfono suena mientras el equipo trabaja, los mensajes llegan con el local cerrado. BOSS quería ofrecer a sus clientes un asistente de IA real, integrado en el software, sin construirlo en casa.')),
    (t('La soluzione','La solución'), t('Odyra ha costruito GoAgent, l\'agente AI che BOSS offre ai saloni col proprio marchio. Risponde al telefono e su WhatsApp 24/7, legge catalogo servizi, operatori e disponibilità di GoWeb e scrive le prenotazioni direttamente in agenda. Odyra ha realizzato anche l\'onboarding automatico dei saloni, la dashboard per i titolari e la piattaforma di gestione dei ricavi condivisi.','Odyra construyó GoAgent, el agente IA que BOSS ofrece a los salones con su marca. Responde al teléfono y por WhatsApp 24/7, lee el catálogo de servicios, operarios y disponibilidad de GoWeb y escribe las reservas directamente en la agenda. Odyra también realizó el onboarding automático de los salones, el panel para los titulares y la plataforma de gestión de ingresos compartidos.')),
    (t('Il risultato','El resultado'), t('In produzione da giugno 2026. Nel salone pilota, 262 chiamate gestite nei primi 15 giorni. BOSS ha aggiunto al proprio gestionale un servizio AI in abbonamento, pronto per l\'intera rete.','En producción desde junio de 2026. En el salón piloto, 262 llamadas gestionadas en los primeros 15 días. BOSS ha añadido a su software un servicio de IA por suscripción, listo para toda la red.')),
  ])}</div></div></div></section>
<section class="sec sec-mist" id="global-trading"><div class="wrap">
  {sportit(True)}
  <h2 style="max-width:22ch;margin-top:34px">{t('L\'agente commerciale che non dorme mai.','El agente comercial que nunca duerme.')}</h2>
  <div class="split" style="margin-top:44px"><div><p class="lead">{t('Global Trading S.r.l. è il gruppo dietro Sportit.com, e-commerce e rete commerciale nel mondo dello sport.','Global Trading S.r.l. es el grupo detrás de Sportit.com, e-commerce y red comercial en el mundo del deporte.')}</p></div>
  <div>{rows([
    (t('La sfida','El reto'), t('Ogni campagna genera centinaia di lead. Richiamarli tutti entro un minuto, in italiano e con la stessa qualità, non è possibile a mano; scalare significava assumere.','Cada campaña genera cientos de leads. Llamarlos a todos en un minuto, en italiano y con la misma calidad, no es posible a mano; escalar significaba contratar.')),
    (t('La soluzione','La solución'), t('Un agente commerciale AI: messaggio di benvenuto immediato su WhatsApp, chiamata entro pochi secondi, qualificazione strutturata, appuntamento fissato nel calendario del team con conferma su WhatsApp, esiti scritti nel CRM aziendale. La collaborazione prosegue con l\'automazione del customer service e-mail per i marketplace.','Un agente comercial IA: mensaje de bienvenida inmediato por WhatsApp, llamada en pocos segundos, calificación estructurada, cita fijada en el calendario del equipo con confirmación por WhatsApp, resultados escritos en el CRM de la empresa. La colaboración continúa con la automatización de la atención por e-mail para marketplaces.')),
    (t('Il risultato','El resultado'), t('Primo contatto sotto il minuto e capacità da 10 a 1.000 chiamate allo stesso costo, indipendente dall\'organico.','Primer contacto en menos de un minuto y capacidad de 10 a 1.000 llamadas al mismo coste, independiente de la plantilla.')),
  ])}</div></div></div></section>'''
    body += cta()
    return layout('casi', t('Casi studio — BOSS e Global Trading · Odyra System', 'Casos de éxito — BOSS y Global Trading · Odyra System'), t('GoAgent per BOSS e l\'agente commerciale per Global Trading: i casi studio di Odyra, con numeri reali.', 'GoAgent para BOSS y el agente comercial para Global Trading: los casos de éxito de Odyra, con números reales.'), body)

# ───────── TECNOLOGIA ─────────
def page_tech():
    body = head_(t('Tecnologia e sicurezza','Tecnología y seguridad'), t('Una piattaforma proprietaria, oltre 18 mesi di lavoro.','Una plataforma propia, más de 18 meses de trabajo.'),
        t('Tutti i prodotti Odyra girano sulla stessa infrastruttura: è la base che permette al gruppo di lanciare nuovi prodotti e nuovi verticali senza ripartire da zero.','Todos los productos de Odyra funcionan sobre la misma infraestructura: es la base que permite al grupo lanzar nuevos productos y verticales sin partir de cero.'))
    body += sec(rows([
      ('Multi-tenant', t('Ogni azienda ha il proprio agente, i propri dati e la propria configurazione, isolati dagli altri, sulla stessa piattaforma.','Cada empresa tiene su propio agente, sus propios datos y su propia configuración, aislados de los demás, sobre la misma plataforma.')),
      (t('Integrazione a connettori','Integración por conectores'), t('Un nuovo gestionale si collega con un connettore dedicato, senza toccare il cuore della piattaforma: più veloce per il partner, più solido per tutti.','Un nuevo software se conecta con un conector dedicado, sin tocar el núcleo de la plataforma: más rápido para el socio, más sólido para todos.')),
      (t('Voce in tempo reale','Voz en tiempo real'), t('Conversazioni naturali in italiano con latenza sotto il secondo.','Conversaciones naturales con latencia inferior al segundo.')),
      (t('Conoscenza dell\'attività','Conocimiento del negocio'), t('Ogni agente risponde a partire dai servizi, dai prezzi e dalle regole dell\'azienda.','Cada agente responde a partir de los servicios, precios y reglas de la empresa.')),
      (t('Infrastruttura privata','Infraestructura privada'), t('Voce e dati girano su infrastruttura dedicata e controllata da Odyra.','Voz y datos funcionan sobre infraestructura dedicada y controlada por Odyra.')),
    ]))
    body += f'''<section class="sec sec-mist" id="whatsapp"><div class="wrap split"><div><h2>{t('WhatsApp Business, gestito dalla piattaforma.','WhatsApp Business, gestionado por la plataforma.')}</h2></div>
      <div><p class="lead">{t('Odyra è Tech Provider Meta tramite Vonage. Attiviamo i numeri, gestiamo template e conversazioni; la titolarità dell\'account resta al cliente.','Odyra es Tech Provider de Meta a través de Vonage. Activamos los números, gestionamos plantillas y conversaciones; la titularidad de la cuenta sigue siendo del cliente.')}</p>
      <div style="display:flex;gap:34px;align-items:center;margin-top:34px"><img src="/assets/logos/whatsapp.svg" alt="WhatsApp" style="height:48px"><img src="/assets/logos/meta.svg" alt="Meta" style="height:32px"><img src="/assets/logos/vonage.svg" alt="Vonage" style="height:32px"></div>
      <p style="margin-top:22px;font-size:.9rem;color:var(--muted)">{t('WhatsApp e Meta sono marchi di Meta Platforms, Inc.; Vonage è un marchio di Vonage Holdings Corp. Odyra non è affiliata a tali società.','WhatsApp y Meta son marcas de Meta Platforms, Inc.; Vonage es una marca de Vonage Holdings Corp. Odyra no está afiliada a dichas empresas.')}</p></div></div></section>'''
    body += sec(f'''<div id="conformita">{sec_head(t('AI Act e GDPR, dal primo giorno.','AI Act y RGPD, desde el primer día.'), t('Per i partner in settori regolati: progettazione nel perimetro di AI Act e GDPR, accordi su dati e cybersecurity, supporto alla documentazione.','Para socios en sectores regulados: diseño dentro del perímetro del AI Act y el RGPD, acuerdos sobre datos y ciberseguridad, apoyo a la documentación.'))}
    <table><tr><th>{t('Trasparenza','Transparencia')}</th><td>{t('L\'utente sa di parlare con un agente AI.','El usuario sabe que habla con un agente de IA.')}</td></tr>
    <tr><th>{t('Escalation umana','Escalada humana')}</th><td>{t('Nei casi delicati la conversazione passa a una persona.','En los casos delicados la conversación pasa a una persona.')}</td></tr>
    <tr><th>{t('Isolamento dei dati','Aislamiento de datos')}</th><td>{t('Dati e configurazione separati per ogni azienda.','Datos y configuración separados para cada empresa.')}</td></tr>
    <tr><th>{t('Registrazioni e report','Grabaciones e informes')}</th><td>{t('Consultabili dal titolare nella dashboard.','Consultables por el titular en el panel.')}</td></tr>
    <tr><th>{t('Documentazione','Documentación')}</th><td>{t('Supporto ai partner per la documentazione richiesta.','Apoyo a los socios en la documentación requerida.')}</td></tr></table></div>''')
    body += cta(t('Domande su sicurezza e conformità?','¿Preguntas sobre seguridad y cumplimiento?'), t('Il nostro team risponde ai tuoi referenti IT e legali.','Nuestro equipo atiende a tus responsables de TI y legal.'))
    return layout('tecnologia', t('Tecnologia e sicurezza — Odyra System', 'Tecnología y seguridad — Odyra System'), t('Piattaforma multi-tenant, voce in tempo reale, WhatsApp Business come Tech Provider Meta, privacy e AI Act by design.', 'Plataforma multi-tenant, voz en tiempo real, WhatsApp Business como Tech Provider de Meta, privacidad y AI Act desde el diseño.'), body)

# ───────── CONTATTI ─────────
def page_contatti():
    opts = [('software-house', t('Partnership per software house','Alianza para software houses')), ('voce', t('Receptionist AI: voce e WhatsApp','Recepcionista IA: voz y WhatsApp')), ('commerciale', t('Agente commerciale AI','Agente comercial IA')), ('hako', 'HAKO'), ('enterprise', 'Enterprise'), ('altro', t('Altro','Otro'))]
    oh = ''.join(f'<option value="{v}">{e(n)}</option>' for v, n in opts)
    body = head_(t('Contatti','Contacto'), t('Parliamo del tuo caso.','Hablemos de tu caso.'), t('Raccontaci come lavori oggi. Ti rispondiamo entro un giorno lavorativo.','Cuéntanos cómo trabajas hoy. Te respondemos en un día laborable.'))
    body += sec(f'''<div class="split split-r"><form class="form" id="form-contatti" novalidate>
    <div class="row"><label>{t('Nome e cognome','Nombre y apellidos')}<input name="nome" required autocomplete="name"></label><label>{t('Azienda','Empresa')}<input name="azienda" required autocomplete="organization"></label></div>
    <div class="row"><label>E-mail<input type="email" name="email" required autocomplete="email"></label><label>{t('Telefono','Teléfono')}<input type="tel" name="telefono" autocomplete="tel"></label></div>
    <label>{t('Di cosa hai bisogno?','¿Qué necesitas?')}<select name="interesse" required>{oh}</select></label>
    <label>{t('Messaggio','Mensaje')}<textarea name="messaggio" placeholder="{t('Che gestionale o CRM usate? Quante chiamate o lead gestite?','¿Qué software o CRM usáis? ¿Cuántas llamadas o leads gestionáis?')}"></textarea></label>
    <input class="hp" name="company_site" tabindex="-1" autocomplete="off" aria-hidden="true">
    <label class="chk"><input type="checkbox" name="privacy" value="si" required><span>{t('Ho letto l\'<a class="link" href="/privacy.html">informativa privacy</a> e acconsento al trattamento dei dati per essere ricontattato.','He leído la <a class="link" href="/es/privacy.html">política de privacidad</a> y consiento el tratamiento de mis datos para ser contactado.')}</span></label>
    <div><button class="btn btn-p" type="submit">{t('Invia la richiesta','Enviar la solicitud')}</button></div>
    <p class="form-msg" id="form-msg" role="status"></p></form>
  <div>{rows([('E-mail', f'<a class="link" href="mailto:{EMAIL}">{EMAIL}</a>'), (t('Sede','Sede'), 'Verypos S.r.l.<br>Viale Papiniano 8<br>20123 Milano (MI)'), (t('Cerchi HAKO?','¿Buscas HAKO?'), f'<a class="link" href="https://hakocondomini.com" rel="noopener">hakocondomini.com</a>')])}</div></div>''')
    return layout('contatti', t('Contatti — Odyra System', 'Contacto — Odyra System'), t('Richiedi una demo o parla con il team Odyra: team@odyrasystemautomation.it, Verypos S.r.l., Milano.', 'Solicita una demo o habla con el equipo de Odyra: team@odyrasystemautomation.it, Verypos S.r.l., Milán.'), body)

def page_privacy():
    body = head_('Privacy', t('Informativa sulla privacy','Política de privacidad'), t('Bozza da far rivedere a un legale prima della pubblicazione.','Borrador que debe revisar un abogado antes de su publicación.'))
    body += sec(rows([
      (t('Titolare del trattamento','Responsable del tratamiento'), f'Verypos S.r.l., Viale Papiniano 8, 20123 Milano — P.IVA 11630390968 — <a class="link" href="mailto:{EMAIL}">{EMAIL}</a>'),
      (t('Dati raccolti','Datos recogidos'), t('Con il modulo contatti raccogliamo nome, azienda, e-mail, telefono e il contenuto del messaggio, al solo scopo di rispondere alla tua richiesta. Il sito non usa cookie di profilazione.','Con el formulario de contacto recogemos nombre, empresa, e-mail, teléfono y el contenido del mensaje, con la única finalidad de responder a tu solicitud. El sitio no usa cookies de perfilado.')),
      (t('Font esterni','Fuentes externas'), t('Il sito carica i caratteri da Google Fonts, che può ricevere il tuo indirizzo IP.','El sitio carga las fuentes desde Google Fonts, que puede recibir tu dirección IP.')),
      (t('I tuoi diritti','Tus derechos'), t('Puoi chiedere accesso, rettifica, cancellazione e opposizione scrivendo a ','Puedes solicitar acceso, rectificación, supresión y oposición escribiendo a ') + EMAIL + '.'),
    ]))
    return layout('contatti', t('Privacy — Odyra System','Privacidad — Odyra System'), t('Informativa sulla privacy di Odyra System.','Política de privacidad de Odyra System.'), body, True, '/privacy.html' if L == 'it' else '/es/privacy.html')

def page_404():
    body = head_('404', t('Qui nessuno risponde.','Aquí nadie responde.'), t('La pagina che cerchi non esiste. Odyra, invece, risponde sempre.','La página que buscas no existe. Odyra, en cambio, responde siempre.'), f'<a class="btn btn-p" href="{url("home")}">{t("Torna alla home","Volver al inicio")}</a>')
    return layout('home', t('Pagina non trovata — Odyra System','Página no encontrada — Odyra System'), t('Pagina non trovata.','Página no encontrada.'), body, True)

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
        return it, ('/es/' + it.lstrip('/') if it != '/' else '/es/')
    sm = ''.join(f'<url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod>' + ''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{SITE}{a}"/>' for l, a in zip(('it', 'es'), alt(u))) + '</url>' for u in urls)
    write('sitemap.xml', f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">{sm}</urlset>\n')
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')

if __name__ == '__main__':
    main()
