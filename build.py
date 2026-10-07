#!/usr/bin/env python3
"""Genera il sito Odyra (italiano in radice, spagnolo in /es/). Uso: python3 build.py"""
import os, html, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://odyrasystemautomation.it'
EMAIL = 'team@odyrasystemautomation.it'
# Indirizzi dei siti dei prodotti: da confermare/aggiornare qui.
LINK_HAKO = 'https://hakocondomini.com'
LINK_BOSS = 'https://bossitalia.com'
LINK_GOAGENT = 'https://bossitalia.com'
L = 'it'

def t(it, es):
    return it if L == 'it' else es

def e(s):
    return html.escape(s, quote=True)

PAGES = [('home', 'index.html'), ('partner', 'per-i-gestionali.html'), ('goagent', 'goagent.html'), ('hako', 'hako.html'),
         ('custom', 'su-misura.html'), ('tech', 'tecnologia.html'), ('gruppo', 'il-gruppo.html'), ('contatti', 'contatti.html')]
FILE = dict(PAGES)

def url(slug, lang=None):
    lang = lang or L
    f = FILE[slug]
    base = '/' if lang == 'it' else '/es/'
    return base if f == 'index.html' else base + f

# ───────── componenti ─────────
def layout(slug, title, desc, body, noindex=False, canonical=None):
    cur = lambda s: ' aria-current="page"' if s == slug else ''
    nav = f'''<nav class="nav" id="nav" aria-label="{t('Principale','Principal')}">
      <a class="nav-link" href="{url('partner')}"{cur('partner')}>{t('Per i gestionali','Para software de gestión')}</a>
      <a class="nav-link" href="{url('goagent')}"{cur('goagent')}>GoAgent</a>
      <a class="nav-link" href="{url('hako')}"{cur('hako')}>HAKO</a>
      <a class="nav-link" href="{url('custom')}"{cur('custom')}>{t('Su misura','A medida')}</a>
      <a class="nav-link" href="{url('tech')}"{cur('tech')}>{t('Tecnologia','Tecnología')}</a>
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
<link rel="stylesheet" href="/styles.css?v=4">
</head>
<body>
<a class="skip" href="#main">{t('Vai al contenuto','Ir al contenido')}</a>
<header class="hdr" id="top"><div class="wrap">
  <a class="brand" href="{url('home')}" aria-label="Odyra System"><img src="/assets/logos/odyra.png" alt="Odyra System" width="167" height="40"></a>
  {nav}
  <button class="burger" id="burger" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
</div></header>
<main id="main">
{body}
</main>
{footer()}
<script src="/script.js?v=4" defer></script>
</body>
</html>
'''

def footer():
    pv = '/privacy.html' if L == 'it' else '/es/privacy.html'
    return f'''<footer class="ftr"><div class="wrap">
  <div class="top">
    <div><img class="flogo" src="/assets/logos/odyra-white.png" alt="Odyra System">
      <p>{t('Agenti AI di settore, in white-label per i gestionali. Software proprietari. Milano.','Agentes IA sectoriales, en white-label para software de gestión. Software propio. Milán.')}</p>
      <div class="partners"><img src="/assets/logos/whatsapp.svg" alt="WhatsApp"><img src="/assets/logos/meta.svg" alt="Meta"><img src="/assets/logos/vonage.svg" alt="Vonage"></div></div>
    <div><h4>{t('Prodotti','Productos')}</h4><ul>
      <li><a href="{url('goagent')}">GoAgent</a></li><li><a href="{url('hako')}">HAKO</a></li><li><a href="{url('custom')}">{t('Su misura','A medida')}</a></li></ul></div>
    <div><h4>Odyra</h4><ul>
      <li><a href="{url('partner')}">{t('Per i gestionali','Para software de gestión')}</a></li><li><a href="{url('tech')}">{t('Tecnologia','Tecnología')}</a></li><li><a href="{url('gruppo')}">{t('Il gruppo','El grupo')}</a></li></ul></div>
    <div><h4>{t('Contatti','Contacto')}</h4><ul>
      <li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li>Verypos S.r.l.<br>Viale Papiniano 8, 20123 Milano</li></ul></div>
  </div>
  <div class="bot"><span>© {datetime.date.today().year} Odyra System · Verypos S.r.l. · P.IVA 11630390968 · REA MI-2615892</span>
  <span><a href="{pv}">Privacy</a> · {t('WhatsApp e Meta sono marchi dei rispettivi proprietari.','WhatsApp y Meta son marcas de sus respectivos propietarios.')}</span></div>
</div></footer>'''

def head_(h1, lead, btns=''):
    return f'<section class="page-head"><div class="wrap"><div><h1>{h1}</h1></div><div><p class="lead">{lead}</p>{("<div class=btns>"+btns+"</div>") if btns else ""}</div></div></section>'

def sec(inner, cls=''):
    return f'<section class="sec {cls}"><div class="wrap">{inner}</div></section>'

def sec_h(h2, p=''):
    return f'<div class="sec-h"><h2>{h2}</h2>{f"<p>{p}</p>" if p else ""}</div>'

def rows(items):
    out = ''
    for it in items:
        title, text = it[0], it[1]
        href = it[2] if len(it) > 2 and it[2] else None
        tag = it[3] if len(it) > 3 else ''
        tg = f'<span class="tag{" tag-live" if len(it) > 4 and it[4] else ""}">{tag}</span>' if tag else ''
        out += f'<a href="{href}"><h3>{title}{tg}</h3><p>{text}</p></a>' if href else f'<div><h3>{title}{tg}</h3><p>{text}</p></div>'
    return f'<div class="rows">{out}</div>'

def steps(items):
    return '<ol class="steps">' + ''.join(f'<li><h3>{a}</h3><p>{b}</p></li>' for a, b in items) + '</ol>'

def rules(items):
    return '<ul class="rules">' + ''.join(f'<li><b>{a}</b> {b}</li>' for a, b in items) + '</ul>'

def vid(name, cap=''):
    ph = t('Il video arriva qui', 'El vídeo llegará aquí')
    return f'''<div><div class="vid" data-vid="{name}"><div class="vid-ph"><span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4l14 8-14 8z"/></svg></span>{ph}</div></div>{f'<p class="vid-cap">{cap}</p>' if cap else ''}</div>'''

def cta(h2=None, p=None, interesse='', btn=None):
    h2 = h2 or t('Parliamo del tuo gestionale.', 'Hablemos de tu software.')
    p = p or t('Ti mostriamo come funziona, con tempi e formula commerciale.', 'Te mostramos cómo funciona, con plazos y fórmula comercial.')
    q = f'?interesse={interesse}' if interesse else ''
    return f'<section class="sec-ink cta"><div class="wrap"><div><h2>{h2}</h2><p>{p}</p></div><div class="btns"><a class="btn btn-w" href="{url("contatti")}{q}">{btn or t("Richiedi una demo","Solicita una demo")}</a></div></div></section>'

def app_demo():
    return f'''<div><div class="demo-tabs" role="group" aria-label="{t('Marchio del gestionale','Marca del software')}"><button data-skin="boss" aria-pressed="true">{t('Con il marchio BOSS','Con la marca BOSS')}</button><button data-skin="partner" aria-pressed="false">{t('Con il tuo marchio','Con tu marca')}</button></div>
<div class="app" id="demo" data-skin="boss" data-slot-empty="{t('Il tuo logo','Tu logo')}" role="img" aria-label="{t('Dimostrazione: un agente AI risponde a una chiamata e scrive la prenotazione nell\'agenda del gestionale','Demostración: un agente IA responde a una llamada y escribe la reserva en la agenda del software')}">
  <div class="app-bar"><span class="dots"><i></i><i></i><i></i></span><span class="app-url">{t('gestionale / agenda','software / agenda')}</span></div>
  <div class="app-body">
    <aside class="app-side"><div class="slot"></div><nav><span class="on">Agenda</span><span>{t('Clienti','Clientes')}</span><span>{t('Servizi','Servicios')}</span><span>{t('Agente AI','Agente IA')}</span></nav></aside>
    <section class="app-main"><h4>{t('Venerdì','Viernes')}</h4>
      <ul class="agenda">
        <li><time>09:00</time><b>Marta B.</b><span>{t('Colore','Color')}</span></li>
        <li><time>10:30</time><b>Luca F.</b><span>{t('Taglio','Corte')}</span></li>
        <li class="free"><time>12:00</time><span>{t('Libero','Libre')}</span><span></span></li>
        <li class="new"><time>15:30</time><b>Elena R.</b><span>{t('Taglio e piega','Corte y peinado')}</span><em>{t('Prenotato dall\'agente AI','Reservado por el agente IA')}</em></li>
      </ul></section>
    <section class="app-call"><div class="call-top"><span class="live">{t('In chiamata','En llamada')}</span><span>21:47</span></div>
      <div class="l ai">{t('Buonasera, Salone Aurora. Sono l\'assistente AI. Come posso aiutarla?','Buenas noches, Salón Aurora. Soy el asistente IA. ¿En qué puedo ayudarle?')}</div>
      <div class="l cl">{t('Vorrei un taglio e piega venerdì pomeriggio.','Quisiera un corte y peinado el viernes por la tarde.')}</div>
      <div class="l ai">{t('Venerdì alle 15:30 con Giulia è libero. Prenoto?','El viernes a las 15:30 con Giulia está libre. ¿Reservo?')}</div>
      <div class="l cl">{t('Sì, grazie.','Sí, gracias.')}</div>
      <div class="wa-chip"><img src="/assets/logos/whatsapp.svg" alt="WhatsApp"><span>{t('Conferma inviata su WhatsApp','Confirmación enviada por WhatsApp')}</span></div></section>
  </div>
</div>
<p class="demo-cap">{t('Stesso agente, marchio diverso. La conversazione è un esempio; BOSS e GoAgent sono un caso reale.','Mismo agente, marca distinta. La conversación es un ejemplo; BOSS y GoAgent son un caso real.')}</p></div>'''

# Regole di mestiere (beauty): sono nel codice, non solo nel prompt.
def beauty_rules(n=None):
    r = [
        (t('Riconosce la cliente dal numero','Reconoce a la clienta por el número'), t('e sa cosa ha fatto di recente. Se due clienti usano lo stesso numero, chiede chi sta parlando.','y sabe qué hizo últimamente. Si dos clientas usan el mismo número, pregunta quién habla.')),
        (t('Prenota più servizi in una sola visita','Reserva varios servicios en una sola visita'), t('cercando uno slot unico, senza buchi tra un servizio e l\'altro.','buscando un único hueco, sin vacíos entre un servicio y otro.')),
        (t('Rispetta l\'ordine tecnico','Respeta el orden técnico'), t('colore, taglio, piega. Schiaritura, tonalizzante, piega. L\'ordine è forzato dal sistema.','color, corte, peinado. Decoloración, tonalizante, peinado. El orden lo fuerza el sistema.')),
        (t('Aggiunge la piega finale','Añade el peinado final'), t('dopo colore, taglio donna e trattamenti, quando serve. Per l\'uomo non la propone.','tras color, corte de mujer y tratamientos, cuando hace falta. Para hombre no lo propone.')),
        (t('Gestisce i pacchetti','Gestiona los paquetes'), t('un servizio ne porta altri, con operatore e ordine fissi, e dice sempre prezzo e durata del trattamento e del totale.','un servicio arrastra otros, con profesional y orden fijos, y dice siempre precio y duración del tratamiento y del total.')),
        (t('Inserisce la consulenza','Inserta la consulta'), t('dove il servizio la richiede, in testa alla sequenza.','donde el servicio la exige, al inicio de la secuencia.')),
        (t('Sceglie l\'operatore','Elige al profesional'), t('rispetta la preferenza della cliente. Con "staff riservato" il salone decide di non far prenotare per nome.','respeta la preferencia de la clienta. Con "equipo reservado" el salón decide no reservar por nombre.')),
        (t('Capisce le fasce orarie','Entiende las franjas horarias'), t('"mattina", "pomeriggio", "dopo le 17", e confronta più giorni alternativi nello stesso messaggio.','"mañana", "tarde", "después de las 17", y compara varios días alternativos en el mismo mensaje.')),
        (t('Prenota solo orari reali','Reserva solo horarios reales'), t('e dice "prenotato" solo dopo la conferma del gestionale.','y dice "reservado" solo tras la confirmación del software.')),
        (t('Sposta senza creare doppioni','Mueve sin crear duplicados'), t('prima prenota il nuovo appuntamento, poi cancella il vecchio.','primero reserva la cita nueva, luego cancela la antigua.')),
        (t('Applica la regola delle 24 ore','Aplica la regla de las 24 horas'), t('entro 24 ore dall\'appuntamento la disdetta passa al salone.','dentro de las 24 horas previas a la cita la cancelación pasa al salón.')),
        (t('Avvisa il salone','Avisa al salón'), t('quando la cliente è in ritardo, sta arrivando o è fuori.','cuando la clienta llega tarde, está llegando o está fuera.')),
        (t('Passa a una persona','Pasa a una persona'), t('quando serve, anche durante la chiamata: l\'operatore entra nella stessa conversazione.','cuando hace falta, incluso durante la llamada: el operador entra en la misma conversación.')),
        (t('Dice sempre di essere un\'AI','Dice siempre que es una IA'), t('in voce e su WhatsApp, come richiede l\'AI Act.','por voz y por WhatsApp, como exige el AI Act.')),
        (t('Segue le regole del salone','Sigue las reglas del salón'), t('clientela riservata, prezzi nascosti, chiusure straordinarie e ferie.','clientela reservada, precios ocultos, cierres extraordinarios y vacaciones.')),
    ]
    return rules(r[:n] if n else r)

# ───────── HOME ─────────
def page_home():
    body = f'''
<section class="hero"><div class="wrap">
  <div>
    <h1>{t('Ogni mestiere ha il suo agente AI. Noi li portiamo dentro i gestionali.','Cada oficio tiene su agente IA. Nosotros los llevamos dentro del software de gestión.')}</h1>
    <p class="lead">{t('Odyra costruisce agenti AI di settore, li collega al software di gestione e li offre ai suoi clienti con il marchio del gestionale.','Odyra construye agentes IA sectoriales, los conecta al software de gestión y los ofrece a sus clientes con la marca del software.')}</p>
    <div class="btns"><a class="btn btn-p" href="{url('partner')}">{t('Diventa partner','Hazte socio')}</a><a class="btn btn-o" href="#video">{t('Guarda il video','Mira el vídeo')}</a></div>
    <div class="proof"><img src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers"><p><b>GoAgent</b> · {t('l\'agente AI di BOSS per la rete GoWeb, più di 1.500 saloni.','el agente IA de BOSS para la red GoWeb, más de 1.500 salones.')}</p></div>
  </div>
  {app_demo()}
</div></section>

<section class="sec" id="video"><div class="wrap split">
  <div><h2>{t('Chi è Odyra, in due minuti.','Quién es Odyra, en dos minutos.')}</h2><p class="lead" style="margin-top:18px">{t('Cosa facciamo, come funziona il programma per i partner e perché un agente di settore è un\'altra cosa rispetto a un\'AI generica.','Qué hacemos, cómo funciona el programa para socios y por qué un agente sectorial es otra cosa frente a una IA genérica.')}</p></div>
  {vid('odyra-presentazione', t('Audio in italiano, sottotitoli selezionabili.','Audio en italiano, subtítulos seleccionables.'))}
</div></section>

<section class="sec"><div class="wrap split">
  <div><h2>{t('Non è un\'AI generica. Conosce il mestiere.','No es una IA genérica. Conoce el oficio.')}</h2>
    <p class="lead" style="margin-top:18px">{t('Le regole del mestiere sono nel codice, non solo in un prompt: l\'agente non le dimentica e non le sbaglia. Nel beauty sono decine. Alcune:','Las reglas del oficio están en el código, no solo en un prompt: el agente no las olvida ni las falla. En beauty son decenas. Algunas:')}</p>
    <p style="margin-top:22px"><a class="link" href="{url('goagent')}">{t('Tutte le funzioni di GoAgent','Todas las funciones de GoAgent')}</a></p></div>
  <div>{beauty_rules(6)}</div>
</div></section>

<section class="sec sec-mist"><div class="wrap">
  {sec_h(t('Come funziona con un gestionale.','Cómo funciona con un software de gestión.'))}
  {steps([
    (t('Ci colleghiamo alle API','Nos conectamos a las API'), t('Leggiamo clienti, servizi, operatori e disponibilità; scriviamo appuntamenti. Il resto della piattaforma non cambia.','Leemos clientes, servicios, profesionales y disponibilidad; escribimos citas. El resto de la plataforma no cambia.')),
    (t('Attiviamo i clienti','Activamos a los clientes'), t('Staff e listino si sincronizzano da soli. Numero, WhatsApp e voce li configura uno specialista Odyra, in circa dieci minuti.','Equipo y tarifas se sincronizan solos. Número, WhatsApp y voz los configura un especialista de Odyra, en unos diez minutos.')),
    (t('Gestiamo tutto','Gestionamos todo'), t('Controlli di qualità, errori, consumi, passaggio a una persona. Il gestionale incassa un canone ricorrente e non gestisce niente.','Controles de calidad, errores, consumos, paso a una persona. El software cobra una cuota recurrente y no gestiona nada.')),
  ])}
  <p style="margin-top:36px"><a class="link" href="{url('partner')}">{t('Il programma per i partner','El programa para socios')}</a></p>
</div></section>

<section class="sec"><div class="wrap">
  {sec_h(t('Un mestiere alla volta.','Un oficio a la vez.'), t('Impariamo un mestiere a fondo e costruiamo l\'agente che lo fa. Lo portiamo ai clienti con i gestionali del settore.','Aprendemos un oficio a fondo y construimos el agente que lo hace. Lo llevamos a los clientes con los software de gestión del sector.'))}
  {rows([
    (t('Beauty','Beauty'), t('GoAgent AI Concierge, con BOSS e GoWeb.','GoAgent AI Concierge, con BOSS y GoWeb.'), url('goagent'), t('In produzione','En producción'), True),
    (t('Dentale','Dental'), t('Prossimo verticale.','Próximo vertical.'), None, t('Prossimo','Próximo')),
    (t('Autofficine','Talleres'), t('Prossimo verticale.','Próximo vertical.'), None, t('Prossimo','Próximo')),
    (t('Ospitalità e veterinari','Hostelería y veterinarios'), t('Prossimi verticali.','Próximos verticales.'), None, t('Prossimo','Próximo')),
  ])}
  <p style="margin-top:28px">{t('Oggi in italiano. Altre lingue e gestionali di altri paesi europei sono nel piano.','Hoy en italiano. Otros idiomas y software de gestión de otros países europeos están en el plan.')}</p>
</div></section>

<section class="sec sec-mist"><div class="wrap split">
  <div><img class="hako-logo" src="/assets/logos/hako.png" alt="HAKO"><h2>{t('Lo stesso metodo, venduto direttamente.','El mismo método, vendido directamente.')}</h2>
    <p class="lead" style="margin-top:18px">{t('HAKO gestisce i pacchi nelle portinerie dei condomini. È un software proprietario di Odyra, costruito sulla stessa piattaforma.','HAKO gestiona los paquetes en las conserjerías de las comunidades. Es un software propio de Odyra, construido sobre la misma plataforma.')}</p>
    <div class="btns"><a class="btn btn-o" href="{url('hako')}">{t('Scopri HAKO','Descubre HAKO')}</a></div></div>
  {vid('hako', '')}
</div></section>

<section class="sec"><div class="wrap split">
  <div><h2>{t('Anche su misura.','También a medida.')}</h2></div>
  <div><p class="lead">{t('Per aziende con grandi volumi costruiamo agenti e automazioni sui loro processi. Per Gruppo Colzani, Sportit.com e Global Trading: un agente che richiama ogni lead in pochi secondi.','Para empresas con grandes volúmenes construimos agentes y automatizaciones sobre sus procesos. Para Gruppo Colzani, Sportit.com y Global Trading: un agente que llama a cada lead en pocos segundos.')}</p>
    <div class="btns"><a class="btn btn-o" href="{url('custom')}">{t('Progetti su misura','Proyectos a medida')}</a></div></div>
</div></section>

{cta()}'''
    return layout('home', t('Odyra System — Agenti AI di settore, in white-label per i gestionali', 'Odyra System — Agentes IA sectoriales, en white-label para software de gestión'),
        t('Odyra costruisce agenti AI di settore, li collega ai gestionali e li offre ai clienti col marchio del gestionale. Con GoAgent per BOSS, primo verticale: beauty.', 'Odyra construye agentes IA sectoriales, los conecta a los software de gestión y los ofrece a los clientes con la marca del software. Con GoAgent para BOSS, primer vertical: beauty.'), body)

# ───────── PER I GESTIONALI ─────────
def page_partner():
    body = head_(t('Un\'AI di settore per i tuoi clienti. Col tuo marchio.','Una IA sectorial para tus clientes. Con tu marca.'),
        t('Il tuo gestionale offre un agente che risponde, prenota e organizza al posto del cliente. Tu porti i clienti, Odyra porta prodotto, tecnologia e gestione.','Tu software ofrece un agente que responde, reserva y organiza en lugar del cliente. Tú aportas los clientes, Odyra aporta producto, tecnología y gestión.'),
        f'<a class="btn btn-p" href="{url("contatti")}?interesse=partner">{t("Diventa partner","Hazte socio")}</a>')
    body += sec(f'<div class="split"><div><h2>{t('Perché non basta un\'AI generica.','Por qué no basta una IA genérica.')}</h2></div><div><p class="lead">{t('I tuoi clienti vogliono l\'AI, ma un\'AI generica non sa cosa vuol dire "colore, taglio e piega in una visita". Odyra costruisce agenti che conoscono il mestiere, perché le regole del settore sono scritte nel codice. Per questo l\'agente diventa tuo: parla come i tuoi clienti, lavora dove lavorano loro.','Tus clientes quieren IA, pero una IA genérica no sabe qué significa "color, corte y peinado en una visita". Odyra construye agentes que conocen el oficio, porque las reglas del sector están escritas en el código. Por eso el agente se vuelve tuyo: habla como tus clientes, trabaja donde ellos trabajan.')}</p></div></div>')
    body += sec(f'''{sec_h(t('Cosa fai tu. Cosa facciamo noi.','Qué haces tú. Qué hacemos nosotros.'))}
      <div class="split split-e"><div>{rows([
        (t('Tu','Tú'), t('Offri il servizio ai tuoi clienti col tuo marchio. Ci dai accesso alle API: ricerca cliente, disponibilità, creazione e cancellazione appuntamenti.','Ofreces el servicio a tus clientes con tu marca. Nos das acceso a las API: búsqueda de cliente, disponibilidad, creación y cancelación de citas.')),
        (t('Il tuo guadagno','Tu ganancia'), t('Un nuovo canone ricorrente da ogni cliente che attiva l\'agente, con revenue condivisa con Odyra.','Una nueva cuota recurrente de cada cliente que activa el agente, con revenue compartida con Odyra.')),
      ])}</div><div>{rows([
        (t('Odyra','Odyra'), t('Agente di settore, connettore col tuo software, onboarding dei clienti, dashboard per i titolari, WhatsApp Business, controlli di qualità e assistenza.','Agente sectorial, conector con tu software, onboarding de clientes, panel para los titulares, WhatsApp Business, controles de calidad y asistencia.')),
        (t('Il tuo marchio','Tu marca'), t('Interfacce, messaggi e dashboard portano il tuo logo.','Interfaces, mensajes y paneles llevan tu logo.')),
      ])}</div></div>''', 'sec-mist')
    body += sec(f'''{sec_h(t('Come si parte.','Cómo se empieza.'))}{steps([
      (t('Collegamento','Conexión'), t('Un connettore dedicato collega il tuo gestionale alla piattaforma, senza toccarne il cuore.','Un conector dedicado conecta tu software con la plataforma, sin tocar su núcleo.')),
      (t('Attivazione dei clienti','Activación de clientes'), t('Staff e listino si sincronizzano da soli. Numero, WhatsApp e voce li configura uno specialista Odyra, in circa dieci minuti.','Equipo y tarifas se sincronizan solos. Número, WhatsApp y voz los configura un especialista de Odyra, en unos diez minutos.')),
      (t('Gestione continua','Gestión continua'), t('Controlliamo qualità, errori e consumi. Il cliente vede tutto nella sua dashboard.','Controlamos calidad, errores y consumos. El cliente lo ve todo en su panel.')),
    ])}''')
    body += sec(f'''<div class="split"><div>{vid('partner-program')}</div><div><h2>{t('Il programma partner, spiegato.','El programa de socios, explicado.')}</h2><p class="lead" style="margin-top:18px">{t('Un video di pochi minuti: cosa include, come funziona e cosa ricevi.','Un vídeo de pocos minutos: qué incluye, cómo funciona y qué recibes.')}</p></div></div>''', 'sec-mist')
    body += sec(f'''{sec_h(t('Un caso reale: BOSS.','Un caso real: BOSS.'))}
      <div class="split"><div><img class="boss-logo" src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers"></div>
      <div><p class="lead">{t('BOSS sviluppa GoWeb, tra i gestionali più diffusi per parrucchieri e centri estetici in Italia, con oltre 1.500 saloni. Con Odyra ha lanciato GoAgent col proprio marchio: risponde al telefono e su WhatsApp e scrive le prenotazioni nell\'agenda di GoWeb.','BOSS desarrolla GoWeb, uno de los software más extendidos entre peluquerías y centros de estética en Italia, con más de 1.500 salones. Con Odyra lanzó GoAgent con su marca: responde al teléfono y por WhatsApp y escribe las reservas en la agenda de GoWeb.')}</p>
      <div class="news"><b>17-19 {t('ottobre','octubre')}</b><span>{t('BOSS inaugura GoAgent alla sua convention, con oltre 300 persone.','BOSS inaugura GoAgent en su convención, con más de 300 personas.')}</span></div>
      <div class="btns"><a class="btn btn-o" href="{url('goagent')}">{t('Vedi GoAgent','Ver GoAgent')}</a></div></div></div>''')
    body += sec(f'''{sec_h(t('Il primo verticale è il beauty. Gli altri seguono.','El primer vertical es beauty. Los demás siguen.'), t('Stessa piattaforma, un mestiere alla volta. Tra i prossimi: dentale, autofficine, ospitalità e veterinari.','Misma plataforma, un oficio a la vez. Entre los próximos: dental, talleres, hostelería y veterinarios.'))}''', 'sec-mist')
    body += cta(t('Porta l\'AI nel tuo gestionale.','Lleva la IA a tu software.'), t('Parliamo di integrazione, formula e tempi.','Hablemos de integración, fórmula y plazos.'), 'partner', t('Diventa partner','Hazte socio'))
    return layout('partner', t('Per i gestionali — AI di settore in white-label · Odyra System', 'Para software de gestión — IA sectorial en white-label · Odyra System'), t('Il tuo gestionale offre un agente AI di settore ai suoi clienti, col tuo marchio. Odyra porta prodotto, tecnologia e gestione.', 'Tu software ofrece un agente IA sectorial a sus clientes, con tu marca. Odyra aporta producto, tecnología y gestión.'), body)

# ───────── GOAGENT ─────────
def page_goagent():
    body = f'''<section class="page-head"><div class="wrap"><div><img class="boss-logo" src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers"><h1>GoAgent AI Concierge</h1></div>
      <div><p class="lead">{t('L\'agente AI di BOSS per i saloni GoWeb. Risponde al telefono e su WhatsApp, giorno e notte, e prenota direttamente nell\'agenda. Costruito da Odyra.','El agente IA de BOSS para los salones GoWeb. Responde al teléfono y por WhatsApp, de día y de noche, y reserva directamente en la agenda. Construido por Odyra.')}</p>
      <div class="btns"><a class="btn btn-p" href="{LINK_GOAGENT}" rel="noopener">{t('Il sito di GoAgent','El sitio de GoAgent')}</a><a class="btn btn-o" href="{url('contatti')}?interesse=goagent">{t('Parla con noi','Habla con nosotros')}</a></div></div></div></section>'''
    body += sec(f'<div class="split"><div><h2>{t('Che cos\'è.','Qué es.')}</h2></div>{vid("goagent", t("Il video di presentazione di GoAgent.","El vídeo de presentación de GoAgent."))}</div>')
    body += sec(f'''{sec_h(t('Parla come un salone, non come un\'AI.','Habla como un salón, no como una IA.'))}
      <div class="split"><div><p class="lead">{t('Frasi brevi, una domanda alla volta, il nome della cliente, la sua ultima visita. Niente "certamente" o "perfetto". Su WhatsApp non chiede mai il numero, che già conosce. Dice sempre di essere un\'assistente AI.','Frases cortas, una pregunta a la vez, el nombre de la clienta, su última visita. Nada de "por supuesto" ni "perfecto". Por WhatsApp nunca pide el número, que ya conoce. Dice siempre que es una asistente IA.')}</p></div>
      <div>{rows([
        (t('Voce e WhatsApp','Voz y WhatsApp'), t('Un solo agente, 24 ore su 24, anche su più conversazioni insieme.','Un solo agente, las 24 horas, también en varias conversaciones a la vez.')),
        (t('Dentro GoWeb','Dentro de GoWeb'), t('Legge servizi, operatori, turni e disponibilità e scrive gli appuntamenti nell\'agenda.','Lee servicios, profesionales, turnos y disponibilidad y escribe las citas en la agenda.')),
        (t('Conferme su WhatsApp','Confirmaciones por WhatsApp'), t('Conferma e disdetta di ogni appuntamento, con messaggi approvati.','Confirmación y cancelación de cada cita, con mensajes aprobados.')),
      ])}</div></div>''', 'sec-mist')
    body += sec(f'''{sec_h(t('Le regole del mestiere.','Las reglas del oficio.'), t('Sono nel codice, non solo in un prompt. Qui ne vedi una parte: ce ne sono molte di più.','Están en el código, no solo en un prompt. Aquí ves una parte: hay muchas más.'))}{beauty_rules()}''')
    body += sec(f'''{sec_h(t('Cosa vede il titolare.','Qué ve el titular.'))}{rows([
      (t('Panoramica','Resumen'), t('Chiamate gestite, appuntamenti fissati dall\'AI, cancellazioni, conversione e ore risparmiate.','Llamadas gestionadas, citas fijadas por la IA, cancelaciones, conversión y horas ahorradas.')),
      (t('Inbox WhatsApp','Bandeja de WhatsApp'), t('Tutte le conversazioni. Il titolare può prenderle in carico, rispondere a mano e ridare la mano all\'AI.','Todas las conversaciones. El titular puede asumirlas, responder a mano y devolver el control a la IA.')),
      (t('Chiamate','Llamadas'), t('Trascrizione, riassunto e dettagli dell\'appuntamento.','Transcripción, resumen y detalles de la cita.')),
      (t('Pacchetti e impostazioni','Paquetes y ajustes'), t('Pacchetti di servizi, voce dell\'assistente, prezzi visibili o nascosti, chiusure straordinarie, consumi del piano.','Paquetes de servicios, voz del asistente, precios visibles u ocultos, cierres extraordinarios, consumos del plan.')),
    ])}''', 'sec-mist')
    body += sec(f'''<div class="split"><div><h2>{t('In arrivo.','Próximamente.')}</h2></div><div><p class="lead">{t('Chiamate in uscita ai clienti che non tornano in salone: l\'agente li richiama, al telefono o su WhatsApp, e li riporta in agenda.','Llamadas salientes a los clientes que no vuelven al salón: el agente los vuelve a llamar, por teléfono o WhatsApp, y los devuelve a la agenda.')}</p>
      <div class="news"><b>17-19 {t('ottobre','octubre')}</b><span>{t('BOSS inaugura GoAgent alla sua convention, con oltre 300 persone.','BOSS inaugura GoAgent en su convención, con más de 300 personas.')}</span></div></div></div>''')
    body += cta(t('Hai un gestionale e vuoi un agente come GoAgent?','¿Tienes un software de gestión y quieres un agente como GoAgent?'), None, 'partner')
    return layout('goagent', t('GoAgent AI Concierge — BOSS e Odyra', 'GoAgent AI Concierge — BOSS y Odyra'), t('GoAgent è l\'agente AI di BOSS per i saloni GoWeb, costruito da Odyra: risponde al telefono e su WhatsApp e prenota nell\'agenda.', 'GoAgent es el agente IA de BOSS para los salones GoWeb, construido por Odyra: responde al teléfono y por WhatsApp y reserva en la agenda.'), body)

# ───────── HAKO ─────────
def page_hako():
    body = f'''<section class="page-head"><div class="wrap"><div><img class="hako-logo" src="/assets/logos/hako.png" alt="HAKO"><h1>{t('Ogni pacco in portineria, ogni condomino avvisato.','Cada paquete en conserjería, cada vecino avisado.')}</h1></div>
      <div><p class="lead">{t('HAKO registra il pacco con una foto, avvisa il destinatario su WhatsApp, SMS o e-mail nella sua lingua e chiude la consegna con un codice di ritiro. Software proprietario di Odyra.','HAKO registra el paquete con una foto, avisa al destinatario por WhatsApp, SMS o e-mail en su idioma y cierra la entrega con un código de recogida. Software propio de Odyra.')}</p>
      <div class="btns"><a class="btn btn-p" href="{LINK_HAKO}" rel="noopener">{t('Il sito di HAKO','El sitio de HAKO')}</a><a class="btn btn-o" href="{url('contatti')}?interesse=hako">{t('Richiedi una demo','Solicita una demo')}</a></div></div></div></section>'''
    body += sec(f'<div class="split"><div><h2>{t('Che cos\'è.','Qué es.')}</h2></div>{vid("hako", t("Il video di presentazione di HAKO.","El vídeo de presentación de HAKO."))}</div>')
    body += sec(f'''{sec_h(t('Tre passaggi, nessun registro cartaceo.','Tres pasos, ningún registro en papel.'))}{steps([
      (t('Il portinaio fotografa il pacco','El conserje fotografía el paquete'), t('HAKO legge destinatario e corriere dall\'etichetta. Il portinaio controlla e conferma.','HAKO lee destinatario y transportista de la etiqueta. El conserje revisa y confirma.')),
      (t('Il condomino riceve l\'avviso','El vecino recibe el aviso'), t('Su WhatsApp, SMS o e-mail, con corriere, condominio e codice di ritiro.','Por WhatsApp, SMS o e-mail, con transportista, comunidad y código de recogida.')),
      (t('Il ritiro si chiude con il codice','La recogida se cierra con el código'), t('Il portinaio registra la consegna. Lo storico resta consultabile.','El conserje registra la entrega. El historial queda consultable.')),
    ])}''', 'sec-mist')
    body += sec(f'''{sec_h(t('Per chi lavora in portineria, per chi amministra, per chi aspetta il pacco.','Para quien trabaja en conserjería, para quien administra, para quien espera el paquete.'))}{rows([
      (t('Il portinaio','El conserje'), t('Lettura dell\'etichetta con la fotocamera, registrazione anche senza connessione, passaggio di consegne a fine turno.','Lectura de la etiqueta con la cámara, registro incluso sin conexión, relevo de turno.')),
      (t('Il condomino','El vecino'), t('Avviso sul canale che preferisce, codice QR di ritiro, delega a un\'altra persona. Nessuna app da installare.','Aviso por el canal que prefiere, código QR de recogida, delegación en otra persona. Sin apps que instalar.')),
      (t('Chi amministra','Quien administra'), t('Storico con foto e orari, solleciti automatici, report, residenti importati da CSV o Excel.','Historial con fotos y horas, recordatorios automáticos, informes, residentes importados desde CSV o Excel.')),
      (t('Privacy','Privacidad'), t('Cancellazione automatica di foto e dati letti, registro delle operazioni, accessi per ruolo, esportazione e cancellazione su richiesta, come previsto dal GDPR.','Borrado automático de fotos y datos leídos, registro de operaciones, accesos por rol, exportación y borrado a petición, como prevé el RGPD.')),
    ])}
    <p style="margin-top:30px">{t('Stiamo aprendo i primi stabili pilota con condizioni dedicate.','Estamos abriendo los primeros edificios piloto con condiciones dedicadas.')}</p>''')
    body += cta(t('Prova HAKO nel tuo stabile.','Prueba HAKO en tu edificio.'), t('Raccontaci come lavorate oggi in portineria.','Cuéntanos cómo trabajáis hoy en conserjería.'), 'hako')
    return layout('hako', t('HAKO — Gestione pacchi per condomini · Odyra', 'HAKO — Gestión de paquetes para comunidades · Odyra'), t('HAKO registra il pacco con una foto e avvisa il condomino su WhatsApp, SMS o e-mail nella sua lingua. Software proprietario di Odyra.', 'HAKO registra el paquete con una foto y avisa al vecino por WhatsApp, SMS o e-mail en su idioma. Software propio de Odyra.'), body)

# ───────── SU MISURA ─────────
def page_custom():
    body = head_(t('Progetti su misura per aziende con grandi volumi.','Proyectos a medida para empresas con grandes volúmenes.'),
        t('Agenti e automazioni disegnati sui processi dell\'azienda: vendite, customer service e back office, integrati con CRM ed ERP.','Agentes y automatizaciones diseñados sobre los procesos de la empresa: ventas, atención al cliente y back office, integrados con CRM y ERP.'),
        f'<a class="btn btn-p" href="{url("contatti")}?interesse=custom">{t("Parliamo del progetto","Hablemos del proyecto")}</a>')
    body += sec(f'''{sec_h(t('Dove l\'AI fa lavoro vero.','Donde la IA hace trabajo real.'))}{rows([
      (t('Vendite','Ventas'), t('Un agente richiama ogni lead in pochi secondi, lo qualifica con domande strutturate e fissa l\'appuntamento nel calendario del team. Chi non risponde al telefono viene recuperato su WhatsApp.','Un agente llama a cada lead en pocos segundos, lo califica con preguntas estructuradas y fija la cita en el calendario del equipo. Quien no contesta al teléfono se recupera por WhatsApp.')),
      (t('Customer service','Atención al cliente'), t('Voce, WhatsApp ed e-mail, con risposte coerenti e passaggio a una persona quando serve.','Voz, WhatsApp y e-mail, con respuestas coherentes y paso a una persona cuando hace falta.')),
      (t('Back office','Back office'), t('Automazioni sui processi ripetitivi, tra i sistemi che l\'azienda usa già.','Automatizaciones en procesos repetitivos, entre los sistemas que la empresa ya usa.')),
    ])}''')
    body += sec(f'''<div class="split"><div><span class="tile"><img src="/assets/logos/sportit.png" alt="Sportit.com"></span><h2 style="margin-top:32px">{t('Gruppo Colzani.','Gruppo Colzani.')}</h2></div>
      <div><p class="lead">{t('Gruppo Colzani, dietro Sportit.com e Global Trading, genera centinaia di lead a ogni campagna. L\'agente commerciale di Odyra scrive subito su WhatsApp, richiama in pochi secondi, qualifica e fissa l\'appuntamento, e scrive l\'esito nel CRM. Si lavora da dieci a mille chiamate allo stesso costo. La collaborazione prosegue con l\'automazione del customer service e-mail per i marketplace.','Gruppo Colzani, detrás de Sportit.com y Global Trading, genera cientos de leads en cada campaña. El agente comercial de Odyra escribe enseguida por WhatsApp, llama en pocos segundos, califica y fija la cita, y escribe el resultado en el CRM. Se trabaja de diez a mil llamadas al mismo coste. La colaboración continúa con la automatización de la atención por e-mail para marketplaces.')}</p></div></div>''', 'sec-mist')
    body += sec(f'''{sec_h(t('Come lavoriamo.','Cómo trabajamos.'))}{steps([
      (t('Capiamo il processo','Entendemos el proceso'), t('Dove si perdono chiamate, tempo e margine.','Dónde se pierden llamadas, tiempo y margen.')),
      (t('Disegniamo e integriamo','Diseñamos e integramos'), t('Cosa sa l\'agente, quando passa la mano a una persona, con quali sistemi si collega.','Qué sabe el agente, cuándo cede el paso a una persona, con qué sistemas se conecta.')),
      (t('Misuriamo','Medimos'), t('Chiamate, esiti e tempi in una dashboard, per migliorare ogni settimana.','Llamadas, resultados y tiempos en un panel, para mejorar cada semana.')),
    ])}''')
    body += cta(t('Hai un processo da automatizzare?','¿Tienes un proceso que automatizar?'), t('Raccontacelo: ti diciamo cosa si può fare e in quanto tempo.','Cuéntanoslo: te decimos qué se puede hacer y en cuánto tiempo.'), 'custom')
    return layout('custom', t('Progetti su misura — Odyra System', 'Proyectos a medida — Odyra System'), t('Agenti e automazioni AI su misura per vendite, customer service e back office, integrati con CRM ed ERP. Caso: Gruppo Colzani.', 'Agentes y automatizaciones IA a medida para ventas, atención al cliente y back office, integrados con CRM y ERP. Caso: Gruppo Colzani.'), body)

# ───────── TECNOLOGIA ─────────
def page_tech():
    body = head_(t('Una piattaforma, tutti i prodotti.','Una plataforma, todos los productos.'),
        t('Oltre 18 mesi di sviluppo di un\'infrastruttura proprietaria: è la base che ci permette di lanciare un nuovo mestiere o un nuovo prodotto senza ripartire da zero.','Más de 18 meses de desarrollo de una infraestructura propia: es la base que nos permite lanzar un nuevo oficio o un nuevo producto sin partir de cero.'))
    body += sec(rows([
      (t('Un agente per cliente','Un agente por cliente'), t('Ogni azienda ha il proprio agente, i propri dati e la propria configurazione, isolati dagli altri, sulla stessa piattaforma.','Cada empresa tiene su propio agente, sus propios datos y su propia configuración, aislados de los demás, sobre la misma plataforma.')),
      (t('Connettori','Conectores'), t('Un nuovo gestionale si collega con un connettore dedicato. La logica di conversazione e le regole di mestiere restano le stesse.','Un nuevo software se conecta con un conector dedicado. La lógica de conversación y las reglas del oficio siguen siendo las mismas.')),
      (t('Voce in tempo reale','Voz en tiempo real'), t('Conversazioni naturali, con risposte senza attese percepibili.','Conversaciones naturales, con respuestas sin esperas perceptibles.')),
      (t('Conoscenza dell\'attività','Conocimiento del negocio'), t('Ogni agente risponde a partire dai servizi, dai prezzi e dalle regole dell\'azienda.','Cada agente responde a partir de los servicios, precios y reglas de la empresa.')),
      (t('Gestione operativa','Gestión operativa'), t('Limiti e avvisi di consumo, controllo di qualità automatico, monitoraggio degli errori con diagnosi, riassunti per il titolare, passaggio a una persona.','Límites y avisos de consumo, control de calidad automático, monitorización de errores con diagnóstico, resúmenes para el titular, paso a una persona.')),
      (t('Infrastruttura','Infraestructura'), t('Voce e dati girano su infrastruttura dedicata e controllata da Odyra.','Voz y datos funcionan sobre infraestructura dedicada y controlada por Odyra.')),
    ]))
    body += sec(f'''<div class="split"><div><h2>WhatsApp Business.</h2></div><div><p class="lead">{t('Odyra è Tech Provider Meta tramite Vonage: attiviamo i numeri, gestiamo template e conversazioni, e la titolarità dell\'account resta al cliente.','Odyra es Tech Provider de Meta a través de Vonage: activamos los números, gestionamos plantillas y conversaciones, y la titularidad de la cuenta sigue siendo del cliente.')}</p>
      <div class="logos" style="margin-top:32px"><img src="/assets/logos/whatsapp.svg" alt="WhatsApp" style="height:46px"><img src="/assets/logos/meta.svg" alt="Meta" style="height:30px"><img src="/assets/logos/vonage.svg" alt="Vonage" style="height:30px"></div>
      <p style="margin-top:20px;font-size:.88rem;color:var(--muted)">{t('WhatsApp e Meta sono marchi di Meta Platforms, Inc.; Vonage è un marchio di Vonage Holdings Corp. Odyra non è affiliata a tali società.','WhatsApp y Meta son marcas de Meta Platforms, Inc.; Vonage es una marca de Vonage Holdings Corp. Odyra no está afiliada a dichas empresas.')}</p></div></div>''', 'sec-mist')
    body += sec(f'''{sec_h(t('AI Act e GDPR, dal primo giorno.','AI Act y RGPD, desde el primer día.'))}<table>
    <tr><th>{t('Trasparenza','Transparencia')}</th><td>{t('L\'agente dice sempre di essere un\'AI, in voce e su WhatsApp.','El agente dice siempre que es una IA, por voz y por WhatsApp.')}</td></tr>
    <tr><th>{t('Passaggio a una persona','Paso a una persona')}</th><td>{t('Nei casi delicati, o quando il cliente lo chiede.','En los casos delicados, o cuando el cliente lo pide.')}</td></tr>
    <tr><th>{t('Dati','Datos')}</th><td>{t('Separati per ogni azienda. Trattamento conforme al GDPR.','Separados para cada empresa. Tratamiento conforme al RGPD.')}</td></tr>
    <tr><th>{t('Documentazione','Documentación')}</th><td>{t('Supporto ai partner nei settori regolati.','Apoyo a los socios en los sectores regulados.')}</td></tr></table>''')
    body += cta(t('Domande su sicurezza e conformità?','¿Preguntas sobre seguridad y cumplimiento?'), t('Rispondiamo ai tuoi referenti IT e legali.','Atendemos a tus responsables de TI y legal.'))
    return layout('tech', t('Tecnologia e sicurezza — Odyra System', 'Tecnología y seguridad — Odyra System'), t('Una piattaforma proprietaria, un agente per cliente, WhatsApp Business come Tech Provider Meta, privacy e AI Act fin dal progetto.', 'Una plataforma propia, un agente por cliente, WhatsApp Business como Tech Provider de Meta, privacidad y AI Act desde el diseño.'), body)

# ───────── IL GRUPPO ─────────
def page_gruppo():
    body = head_(t('Un metodo: un mestiere alla volta.','Un método: un oficio a la vez.'),
        t('Odyra è un gruppo tecnologico milanese. Impariamo un mestiere a fondo e costruiamo il software con l\'AI che lo fa. Lo portiamo ai clienti in due modi.','Odyra es un grupo tecnológico milanés. Aprendemos un oficio a fondo y construimos el software con IA que lo hace. Lo llevamos a los clientes de dos maneras.'))
    body += sec(rows([
      (t('Con i gestionali','Con los software de gestión'), t('Agenti di settore in white-label dentro il software che i clienti usano già. Primo verticale: beauty, con GoAgent di BOSS.','Agentes sectoriales en white-label dentro del software que los clientes ya usan. Primer vertical: beauty, con GoAgent de BOSS.'), url('partner')),
      (t('In proprio','Por cuenta propia'), t('Software proprietari venduti direttamente. HAKO per le portinerie dei condomini, e altri in arrivo.','Software propio vendido directamente. HAKO para las conserjerías de las comunidades, y otros en camino.'), url('hako')),
      (t('Su misura','A medida'), t('Agenti e automazioni per aziende con grandi volumi.','Agentes y automatizaciones para empresas con grandes volúmenes.'), url('custom')),
    ]))
    body += sec(f'''{sec_h(t('Missione e visione.','Misión y visión.'))}{rows([
      (t('Missione','Misión'), t('Dare a ogni azienda, dal singolo salone al gruppo industriale, una forza di lavoro AI affidabile, integrata e misurabile.','Dar a cada empresa, del salón individual al grupo industrial, una fuerza de trabajo de IA fiable, integrada y medible.')),
      (t('Visione','Visión'), t('Diventare il gruppo europeo di riferimento per i software AI verticali: prodotti proprietari, ciascuno leader nel proprio mercato, su un\'unica infrastruttura condivisa.','Convertirnos en el grupo europeo de referencia del software de IA vertical: productos propios, cada uno líder en su mercado, sobre una única infraestructura compartida.')),
    ])}''', 'sec-mist')
    body += sec(f'<table><tr><th>{t("Società","Sociedad")}</th><td>Verypos S.r.l.</td></tr><tr><th>{t("Sede","Sede")}</th><td>Viale Papiniano 8, 20123 Milano</td></tr><tr><th>{t("Contatto","Contacto")}</th><td><a class="link" href="mailto:{EMAIL}">{EMAIL}</a></td></tr></table>')
    body += cta(t('Lavoriamo insieme.','Trabajemos juntos.'), t('Che tu sia un gestionale o un\'azienda, raccontaci il tuo caso.','Seas un software de gestión o una empresa, cuéntanos tu caso.'))
    return layout('gruppo', t('Il gruppo — Odyra System', 'El grupo — Odyra System'), t('Odyra impara un mestiere alla volta e costruisce il software con l\'AI che lo fa: con i gestionali, in proprio e su misura.', 'Odyra aprende un oficio a la vez y construye el software con IA que lo hace: con software de gestión, por cuenta propia y a medida.'), body)

# ───────── CONTATTI / PRIVACY / 404 ─────────
def page_contatti():
    opts = [('partner', t('Partnership per gestionali','Alianza para software de gestión')), ('goagent', 'GoAgent'), ('hako', 'HAKO'), ('custom', t('Progetto su misura','Proyecto a medida')), ('altro', t('Altro','Otro'))]
    oh = ''.join(f'<option value="{v}">{e(n)}</option>' for v, n in opts)
    body = head_(t('Parliamo del tuo caso.','Hablemos de tu caso.'), t('Raccontaci come lavori oggi. Ti rispondiamo entro un giorno lavorativo.','Cuéntanos cómo trabajas hoy. Te respondemos en un día laborable.'))
    body += sec(f'''<div class="split split-e"><form class="form" id="form-contatti" novalidate>
    <div class="row"><label>{t('Nome e cognome','Nombre y apellidos')}<input name="nome" required autocomplete="name"></label><label>{t('Azienda','Empresa')}<input name="azienda" required autocomplete="organization"></label></div>
    <div class="row"><label>E-mail<input type="email" name="email" required autocomplete="email"></label><label>{t('Telefono','Teléfono')}<input type="tel" name="telefono" autocomplete="tel"></label></div>
    <label>{t('Di cosa hai bisogno?','¿Qué necesitas?')}<select name="interesse" required>{oh}</select></label>
    <label>{t('Messaggio','Mensaje')}<textarea name="messaggio" placeholder="{t('Che gestionale sviluppate? Quanti clienti avete?','¿Qué software desarrolláis? ¿Cuántos clientes tenéis?')}"></textarea></label>
    <input class="hp" name="company_site" tabindex="-1" autocomplete="off" aria-hidden="true">
    <label class="chk"><input type="checkbox" name="privacy" value="si" required><span>{t('Ho letto l\'<a class="link" href="/privacy.html">informativa privacy</a> e acconsento al trattamento dei dati per essere ricontattato.','He leído la <a class="link" href="/es/privacy.html">política de privacidad</a> y consiento el tratamiento de mis datos para ser contactado.')}</span></label>
    <div><button class="btn btn-p" type="submit">{t('Invia la richiesta','Enviar la solicitud')}</button></div>
    <p class="form-msg" id="form-msg" role="status"></p></form>
  <div>{rows([('E-mail', f'<a class="link" href="mailto:{EMAIL}">{EMAIL}</a>'), (t('Sede','Sede'), 'Verypos S.r.l.<br>Viale Papiniano 8<br>20123 Milano (MI)')])}</div></div>''')
    return layout('contatti', t('Contatti — Odyra System', 'Contacto — Odyra System'), t('Parla con il team Odyra: team@odyrasystemautomation.it, Verypos S.r.l., Milano.', 'Habla con el equipo de Odyra: team@odyrasystemautomation.it, Verypos S.r.l., Milán.'), body)

def page_privacy():
    body = head_(t('Informativa sulla privacy','Política de privacidad'), t('Bozza da far rivedere a un legale prima della pubblicazione.','Borrador que debe revisar un abogado antes de su publicación.'))
    body += sec(rows([
      (t('Titolare del trattamento','Responsable del tratamiento'), f'Verypos S.r.l., Viale Papiniano 8, 20123 Milano — P.IVA 11630390968 — <a class="link" href="mailto:{EMAIL}">{EMAIL}</a>'),
      (t('Dati raccolti','Datos recogidos'), t('Con il modulo contatti raccogliamo nome, azienda, e-mail, telefono e il messaggio, al solo scopo di rispondere alla tua richiesta. Il sito non usa cookie di profilazione.','Con el formulario de contacto recogemos nombre, empresa, e-mail, teléfono y el mensaje, con la única finalidad de responder a tu solicitud. El sitio no usa cookies de perfilado.')),
      (t('Font esterni','Fuentes externas'), t('Il sito carica i caratteri da Google Fonts, che può ricevere il tuo indirizzo IP.','El sitio carga las fuentes desde Google Fonts, que puede recibir tu dirección IP.')),
      (t('I tuoi diritti','Tus derechos'), t('Puoi chiedere accesso, rettifica, cancellazione e opposizione scrivendo a ','Puedes solicitar acceso, rectificación, supresión y oposición escribiendo a ') + EMAIL + '.'),
    ]))
    return layout('contatti', t('Privacy — Odyra System','Privacidad — Odyra System'), t('Informativa sulla privacy di Odyra System.','Política de privacidad de Odyra System.'), body, True, '/privacy.html' if L == 'it' else '/es/privacy.html')

def page_404():
    body = head_('404', t('La pagina che cerchi non esiste.','La página que buscas no existe.'), f'<a class="btn btn-p" href="{url("home")}">{t("Torna alla home","Volver al inicio")}</a>')
    return layout('home', t('Pagina non trovata — Odyra System','Página no encontrada — Odyra System'), t('Pagina non trovata.','Página no encontrada.'), body, True)

BUILDERS = {'home': page_home, 'partner': page_partner, 'goagent': page_goagent, 'hako': page_hako, 'custom': page_custom, 'tech': page_tech, 'gruppo': page_gruppo, 'contatti': page_contatti}

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
