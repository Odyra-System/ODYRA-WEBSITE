#!/usr/bin/env python3
"""Genera il sito Odyra (italiano in radice, spagnolo in /es/). Uso: python3 build.py"""
import os, html, datetime, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://odyrasystemautomation.it'
EMAIL = 'team@odyrasystemautomation.it'
# Indirizzi esterni: da confermare/aggiornare qui.
LINK_HAKO = 'https://hakocondomini.com'
LINK_BOSS = 'https://bossitalia.com'
L = 'it'

def t(it, es):
    return it if L == 'it' else es

def e(s):
    return html.escape(s, quote=True)

PAGES = [('home', 'index.html'), ('piattaforma', 'piattaforma.html'), ('settori', 'settori.html'), ('partner', 'per-i-gestionali.html'),
         ('goagent', 'goagent.html'), ('custom', 'su-misura.html'), ('gruppo', 'il-gruppo.html'), ('contatti', 'contatti.html')]
FILE = dict(PAGES)

def url(slug, lang=None):
    lang = lang or L
    f = FILE[slug]
    base = '/' if lang == 'it' else '/es/'
    return base if f == 'index.html' else base + f

# ───────── struttura comune ─────────
def head_tags(slug, title, desc, noindex, canonical, goagent):
    path = canonical or url(slug)
    alt = ''.join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{url(slug, l)}">' for l in ('it', 'es')) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{url(slug, "it")}">'
    robots = '<meta name="robots" content="noindex">' if noindex else ''
    fonts = 'family=Poppins:wght@600;700;800&family=Lato:wght@400;700' if goagent else 'family=Oxanium:wght@500;600;700&family=Inter:wght@400;500;600'
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{robots}<link rel="canonical" href="{SITE}{path}">
{alt}
<meta property="og:type" content="website"><meta property="og:site_name" content="Odyra System">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE}{path}"><meta property="og:image" content="{SITE}/assets/og-v2.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{'#2B1F73' if goagent else '#04132E'}">
<link rel="icon" href="/assets/favicon-v2.ico" sizes="any"><link rel="icon" href="/assets/fav-48.png" type="image/png" sizes="48x48"><link rel="apple-touch-icon" href="/assets/fav-180.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fonts}&display=swap">
<link rel="stylesheet" href="/styles.css?v=7">'''

def lang_switch(slug):
    return f'<div class="lang" role="group" aria-label="Lingua"><a href="{url(slug,"it")}" hreflang="it"{" aria-current=true" if L=="it" else ""}>IT</a><a href="{url(slug,"es")}" hreflang="es"{" aria-current=true" if L=="es" else ""}>ES</a></div>'

def layout(slug, title, desc, body, noindex=False, canonical=None, goagent=False):
    cur = lambda s: ' aria-current="page"' if s == slug else ''
    if goagent:
        header = f'''<header class="hdr" id="top"><div class="wrap">
  <a class="brand ga-brand" href="{url('goagent')}" aria-label="GoAgent"><span class="ga-mark">G</span><span class="ga-name">GoAgent</span></a>
  <nav class="nav" id="nav" aria-label="{t('Principale','Principal')}">
    <a class="nav-link" href="#storia">{t('La storia','La historia')}</a><a class="nav-link" href="#funzioni">{t('Funzioni','Funciones')}</a><a class="nav-link" href="#dashboard">{t('Dashboard','Panel')}</a>
    {lang_switch(slug)}
    <a class="btn btn-p btn-sm" href="{LINK_BOSS}" rel="noopener">{t('Vai a BOSS','Ir a BOSS')}</a>
  </nav>
  <button class="burger" id="burger" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
</div></header>'''
        foot = f'''<footer class="ftr"><div class="wrap"><div class="ga-foot"><p>{t('GoAgent è il servizio AI di BOSS per i saloni GoWeb. Sviluppato e gestito da','GoAgent es el servicio IA de BOSS para los salones GoWeb. Desarrollado y gestionado por')}</p><a href="{url('home')}" aria-label="Odyra System"><img class="flogo" src="/assets/logos/odyra-system.png" alt="Odyra System"></a></div>
<div class="bot"><span>© {datetime.date.today().year} Odyra System · Verypos S.r.l. · P.IVA 11630390968</span><span><a href="{LINK_BOSS}" rel="noopener">BOSS</a> · <a href="{url('home')}">odyra</a> · <a href="{'/privacy.html' if L=='it' else '/es/privacy.html'}">Privacy</a></span></div></div></footer>'''
    else:
        header = f'''<header class="hdr" id="top"><div class="wrap">
  <a class="brand" href="{url('home')}" aria-label="Odyra System"><img src="/assets/logos/odyra-system.png" alt="Odyra System" width="163" height="44"></a>
  <nav class="nav" id="nav" aria-label="{t('Principale','Principal')}">
    <a class="nav-link" href="{url('piattaforma')}"{cur('piattaforma')}>{t('Piattaforma','Plataforma')}</a>
    <a class="nav-link" href="{url('settori')}"{cur('settori')}>{t('Settori','Sectores')}</a>
    <a class="nav-link" href="{url('partner')}"{cur('partner')}>{t('Per i partner','Para socios')}</a>
    <a class="nav-link" href="{url('custom')}"{cur('custom')}>{t('Su misura','A medida')}</a>
    <a class="nav-link" href="{url('gruppo')}"{cur('gruppo')}>{t('Il gruppo','El grupo')}</a>
    {lang_switch(slug)}
    <a class="btn btn-p btn-sm" href="{url('contatti')}">{t('Parla con noi','Habla con nosotros')}</a>
  </nav>
  <button class="burger" id="burger" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
</div></header>'''
        foot = footer()
    return f'''<!doctype html>
<html lang="{L}">
<head>
{head_tags(slug, title, desc, noindex, canonical, goagent)}
</head>
<body{' class="t-goagent"' if goagent else ''}>
<a class="skip" href="#main">{t('Vai al contenuto','Ir al contenido')}</a>
{header}
<main id="main">
{body}
</main>
{foot}
<script src="/script.js?v=7" defer></script>
</body>
</html>
'''

def footer():
    pv = '/privacy.html' if L == 'it' else '/es/privacy.html'
    return f'''<footer class="ftr"><div class="wrap">
  <div class="top">
    <div><img class="flogo" src="/assets/logos/odyra-system.png" alt="Odyra System">
      <p>{t('Agenti AI di settore, in white-label per i software di gestione. Software proprietari. Milano.','Agentes IA sectoriales, en white-label para software de gestión. Software propio. Milán.')}</p>
      <div class="partners"><img src="/assets/logos/whatsapp.svg" alt="WhatsApp"><img src="/assets/logos/meta.svg" alt="Meta"><img src="/assets/logos/vonage.svg" alt="Vonage"></div></div>
    <div><h4>Odyra</h4><ul><li><a href="{url('piattaforma')}">{t('Piattaforma','Plataforma')}</a></li><li><a href="{url('settori')}">{t('Settori','Sectores')}</a></li><li><a href="{url('partner')}">{t('Per i partner','Para socios')}</a></li><li><a href="{url('custom')}">{t('Su misura','A medida')}</a></li><li><a href="{url('gruppo')}">{t('Il gruppo','El grupo')}</a></li></ul></div>
    <div><h4>{t('Costruito con Odyra','Construido con Odyra')}</h4><ul><li><a href="{url('goagent')}">GoAgent</a></li><li><a href="{LINK_HAKO}" rel="noopener">HAKO ↗</a></li></ul></div>
    <div><h4>{t('Contatti','Contacto')}</h4><ul><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li>Verypos S.r.l.<br>Viale Papiniano 8, 20123 Milano</li></ul></div>
  </div>
  <div class="bot"><span>© {datetime.date.today().year} Odyra System · Verypos S.r.l. · P.IVA 11630390968 · REA MI-2615892</span>
  <span><a href="{pv}">Privacy</a> · {t('WhatsApp e Meta sono marchi dei rispettivi proprietari.','WhatsApp y Meta son marcas de sus respectivos propietarios.')}</span></div>
</div></footer>'''

def head_(h1, lead, btns=''):
    return f'<section class="page-head"><div class="wrap"><div><h1>{h1}</h1></div><div><p class="lead">{lead}</p>{("<div class=btns>"+btns+"</div>") if btns else ""}</div></div></section>'

def sec(inner, cls=''):
    return f'<section class="sec {cls}"><div class="wrap">{inner}</div></section>'

def sec_h(h2, p='', center=False):
    return f'<div class="sec-h{" center" if center else ""}"><h2>{h2}</h2>{f"<p>{p}</p>" if p else ""}</div>'

def rows(items):
    out = ''
    for it in items:
        title, text = it[0], it[1]
        href = it[2] if len(it) > 2 and it[2] else None
        tag = it[3] if len(it) > 3 else ''
        tg = f'<span class="tag{" tag-live" if len(it) > 4 and it[4] else ""}">{tag}</span>' if tag else ''
        out += f'<a href="{href}"><h3>{title}{tg}</h3><p>{text}</p></a>' if href else f'<div><h3>{title}{tg}</h3><p>{text}</p></div>'
    return f'<div class="rows">{out}</div>'

def steps(items, n=None):
    return f'<ol class="steps s{n or len(items)}">' + ''.join(f'<li><h3>{a}</h3><p>{b}</p></li>' for a, b in items) + '</ol>'

def rules(items):
    return '<ul class="rules">' + ''.join(f'<li><b>{a}</b> {b}</li>' for a, b in items) + '</ul>'

def vid(name, cap=''):
    ph = t('Il video arriva qui', 'El vídeo llegará aquí')
    return f'''<div><div class="vid" data-vid="{name}"><div class="vid-ph"><span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4l14 8-14 8z"/></svg></span>{ph}</div></div>{f'<p class="vid-cap">{cap}</p>' if cap else ''}</div>'''

def cta(h2=None, p=None, interesse='', btn=None):
    h2 = h2 or t('Parliamo del tuo software.', 'Hablemos de tu software.')
    p = p or t('Ti mostriamo come funziona, con tempi e formula commerciale.', 'Te mostramos cómo funciona, con plazos y fórmula comercial.')
    q = f'?interesse={interesse}' if interesse else ''
    return f'<section class="cta"><div class="wrap"><div><h2>{h2}</h2><p>{p}</p></div><div class="btns"><a class="btn btn-w" href="{url("contatti")}{q}">{btn or t("Richiedi una demo","Solicita una demo")}</a></div></div></section>'

def chips(items):
    return '<div class="chips">' + ''.join(f'<span>{i}</span>' for i in items) + '</div>'

def hero_art():
    rows_ = [(640, 330, 190), (560, 290, 150), (480, 250, 230), (400, 210, 170), (320, 170, 260)]
    out = ''
    for y, ye, x0 in rows_:
        xa = 640 - (y - ye)
        out += f'<path d="M{x0} {y} H{xa} L640 {ye}" fill="none" stroke="#123B73" stroke-width="2"/><circle cx="{x0}" cy="{y}" r="9" fill="#04132E" stroke="#1B5AA8" stroke-width="2"/>'
    return f'<div class="hero-art" aria-hidden="true"><svg viewBox="0 0 640 760" preserveAspectRatio="xMaxYMid slice">{out}</svg></div>'

def verts():
    names = [t('Beauty', 'Beauty'), t('Dentale', 'Dental'), t('Autofficine', 'Talleres'), t('Ospitalità', 'Hostelería'), t('Veterinari', 'Veterinarios'), t('Altri settori', 'Otros sectores')]
    return '<ul class="verts">' + ''.join(f'<li class="on"><b>{n}</b></li>' for n in names) + '</ul>'

def platform_diagram():
    sectors = [t('Beauty', 'Beauty'), t('Dentale', 'Dental'), t('Autofficine', 'Talleres'), t('Ospitalità', 'Hostelería'), t('Veterinari', 'Veterinarios'), '…']
    layers = [t('Regole di settore', 'Reglas de sector'), t('Connettori ai software di gestione', 'Conectores a los software de gestión'), t('Voce e WhatsApp', 'Voz y WhatsApp'), t('Gestione operativa', 'Gestión operativa'), 'AI Act · GDPR']
    ls = ''.join(f'<li>{x}</li>' for x in layers)
    return f'''<div class="plat" role="img" aria-label="{t('Schema: i settori entrano nella piattaforma Odyra, che porta gli agenti ai software di gestione e ai loro clienti.','Esquema: los sectores entran en la plataforma Odyra, que lleva los agentes a los software de gestión y a sus clientes.')}">
  <div class="pl-box"><small>{t('Settori di competenza','Sectores de competencia')}</small>{chips(sectors)}</div>
  <div class="pl-line"><i></i></div>
  <div class="pl-core"><div class="pl-title"><img src="/assets/logos/odyra-mark.png" alt=""><b>{t('Piattaforma Odyra','Plataforma Odyra')}</b></div><ul>{ls}</ul></div>
  <div class="pl-line"><i></i></div>
  <div class="pl-box"><small>{t('Software di gestione, col loro marchio','Software de gestión, con su marca')}</small>
    <div class="pl-slots"><span class="pl-logo"><img src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers"></span><span class="pl-brand">{t('Il marchio del software','La marca del software')}</span></div></div>
  <div class="pl-line"><i></i></div>
  <div class="pl-end">{t('I clienti del software di gestione','Los clientes del software de gestión')}</div>
</div>'''

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
<section class="hero"><div class="wrap hero-grid">
  <div>
    <h1>{t('Ogni settore ha il suo agente AI. Noi li portiamo dentro i software di gestione.','Cada sector tiene su agente IA. Nosotros los llevamos dentro de los software de gestión.')}</h1>
    <p class="lead">{t('Odyra costruisce agenti AI di settore, li collega ai software di gestione e li offre ai loro clienti con il marchio del software.','Odyra construye agentes IA sectoriales, los conecta a los software de gestión y los ofrece a sus clientes con la marca del software.')}</p>
    <div class="btns"><a class="btn btn-p" href="{url('partner')}">{t('Diventa partner','Hazte socio')}</a><a class="btn btn-o" href="#video">{t('Guarda il video','Mira el vídeo')}</a></div>
  </div>
  {platform_diagram()}
</div></section>

<section class="sec sec-alt" id="video"><div class="wrap">
  {sec_h(t('Chi è Odyra, in due minuti.','Quién es Odyra, en dos minutos.'), t('Cosa facciamo, come funziona il programma per i partner e perché un agente di settore è un\'altra cosa rispetto a un\'AI generica.','Qué hacemos, cómo funciona el programa para socios y por qué un agente sectorial es otra cosa frente a una IA genérica.'), True)}
  <div class="vid-wide">{vid('odyra-presentazione', t('Audio in italiano, sottotitoli selezionabili.','Audio en italiano, subtítulos seleccionables.'))}</div>
</div></section>

<section class="sec"><div class="wrap">
  {sec_h(t('Il modello, in quattro mosse.','El modelo, en cuatro movimientos.'))}
  {steps([
    (t('Scegliamo un settore','Elegimos un sector'), t('E lo studiamo a fondo: come lavora, cosa chiedono i clienti, quali regole contano.','Y lo estudiamos a fondo: cómo trabaja, qué piden los clientes, qué reglas cuentan.')),
    (t('Costruiamo l\'agente','Construimos el agente'), t('Le regole del settore entrano nel codice, non solo in un prompt.','Las reglas del sector entran en el código, no solo en un prompt.')),
    (t('Ci colleghiamo','Nos conectamos'), t('Alle API dei software di gestione di quel settore.','A las API de los software de gestión de ese sector.')),
    (t('Il software lo offre','El software lo ofrece'), t('Ai suoi clienti, col suo marchio. Incassa un canone ricorrente. Odyra gestisce tutto il resto.','A sus clientes, con su marca. Cobra una cuota recurrente. Odyra gestiona todo lo demás.')),
  ])}
</div></section>

<section class="sec sec-alt"><div class="wrap split">
  <div><h2>{t('Perché non basta un\'AI generica.','Por qué no basta una IA genérica.')}</h2></div>
  <div>{rows([
    (t('Conosce il settore','Conoce el sector'), t('Le regole di chi fa quel lavoro sono scritte nel codice: l\'agente non le dimentica e non le sbaglia.','Las reglas de quien hace ese trabajo están escritas en el código: el agente no las olvida ni las falla.')),
    (t('Lavora dove lavorano già','Trabaja donde ya trabajan'), t('Legge e scrive nel software di gestione. Nessun nuovo strumento da imparare.','Lee y escribe en el software de gestión. Ninguna herramienta nueva que aprender.')),
    (t('È gestita','Está gestionada'), t('Qualità, errori, consumi e passaggio a una persona li gestiamo noi, per ogni cliente.','Calidad, errores, consumos y paso a una persona los gestionamos nosotros, para cada cliente.')),
  ])}<p style="margin-top:28px"><a class="link" href="{url('piattaforma')}">{t('La piattaforma','La plataforma')}</a></p></div>
</div></section>

<section class="sec"><div class="wrap">
  {sec_h(t('Settori di competenza.','Sectores de competencia.'), t('Studiamo a fondo ogni settore prima di costruire l\'agente: come si lavora, cosa chiedono i clienti, quali regole contano.','Estudiamos a fondo cada sector antes de construir el agente: cómo se trabaja, qué piden los clientes, qué reglas cuentan.'))}
  {verts()}
  <p style="margin-top:36px"><a class="link" href="{url('settori')}">{t('Tutti i settori','Todos los sectores')}</a></p>
</div></section>

<section class="sec sec-alt"><div class="wrap">
  {sec_h(t('Costruito con la nostra piattaforma.','Construido con nuestra plataforma.'))}
  <div class="tiles">
    <a class="tilecard" href="{url('goagent')}"><img class="tl" src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers"><h3>GoAgent</h3><p>{t('L\'agente AI di BOSS per i saloni GoWeb. Il nostro punto di riferimento nel beauty.','El agente IA de BOSS para los salones GoWeb. Nuestro referente en beauty.')}</p><span class="more">{t('Scopri GoAgent','Descubre GoAgent')}</span></a>
    <a class="tilecard" href="{LINK_HAKO}" rel="noopener"><img class="tl w" src="/assets/logos/hako-white.png" alt="HAKO"><h3>HAKO</h3><p>{t('Software proprietario di Odyra per le portinerie dei condomini. Ha il suo sito.','Software propio de Odyra para las conserjerías de las comunidades. Tiene su propio sitio.')}</p><span class="more">hakocondomini.com ↗</span></a>
    <a class="tilecard" href="{url('custom')}"><span class="tile tl"><img src="/assets/logos/sportit.png" alt="Sportit.com"></span><h3>{t('Progetti su misura','Proyectos a medida')}</h3><p>{t('Agenti e automazioni per aziende con grandi volumi, come Gruppo Colzani.','Agentes y automatizaciones para empresas con grandes volúmenes, como Gruppo Colzani.')}</p><span class="more">{t('Scopri i progetti','Descubre los proyectos')}</span></a>
  </div>
</div></section>

<section class="sec"><div class="wrap split">
  <div><h2>{t('Canali ufficiali.','Canales oficiales.')}</h2></div>
  <div><p class="lead">{t('Odyra è Tech Provider Meta tramite Vonage: attiviamo i numeri WhatsApp Business, gestiamo template e conversazioni, e la titolarità dell\'account resta al cliente.','Odyra es Tech Provider de Meta a través de Vonage: activamos los números de WhatsApp Business, gestionamos plantillas y conversaciones, y la titularidad de la cuenta sigue siendo del cliente.')}</p>
    <div class="logos" style="margin-top:28px"><img src="/assets/logos/whatsapp.svg" alt="WhatsApp" style="height:44px"><img src="/assets/logos/meta.svg" alt="Meta" style="height:28px"><img src="/assets/logos/vonage.svg" alt="Vonage" style="height:28px"></div></div>
</div></section>

{cta()}'''
    return layout('home', t('Odyra System — Agenti AI di settore, in white-label per i software di gestione', 'Odyra System — Agentes IA sectoriales, en white-label para software de gestión'),
        t('Odyra costruisce agenti AI di settore, li collega ai software di gestione e li offre ai clienti col marchio del software. ', 'Odyra construye agentes IA sectoriales, los conecta a los software de gestión y los ofrece a los clientes con la marca del software. '), body)

# ───────── PIATTAFORMA ─────────
def page_piattaforma():
    body = head_(t('Una piattaforma. Cinque strati.','Una plataforma. Cinco capas.'),
        t('Oltre 18 mesi di sviluppo di un\'infrastruttura proprietaria: è la base che ci permette di lanciare un nuovo settore o un nuovo prodotto senza ripartire da zero.','Más de 18 meses de desarrollo de una infraestructura propia: es la base que nos permite lanzar un nuevo sector o un nuevo producto sin partir de cero.'))
    body += sec(rows([
        (t('1. Regole di settore','1. Reglas de sector'), t('Il cuore: come lavora quel settore, scritto nel codice. Ordine dei servizi, pacchetti, politiche di disdetta, scelta dell\'operatore, passaggio a una persona. Cambia da settore a settore; il resto della piattaforma no.','El núcleo: cómo trabaja ese sector, escrito en el código. Orden de los servicios, paquetes, políticas de cancelación, elección del profesional, paso a una persona. Cambia de un sector a otro; el resto de la plataforma no.')),
        (t('2. Connettori','2. Conectores'), t('Un connettore dedicato per ogni software di gestione: legge clienti, servizi, operatori e disponibilità, scrive e cancella appuntamenti. Per aggiungere un nuovo software si scrive il connettore; logica di conversazione e regole restano le stesse.','Un conector dedicado para cada software de gestión: lee clientes, servicios, profesionales y disponibilidad, escribe y cancela citas. Para añadir un nuevo software se escribe el conector; lógica de conversación y reglas siguen siendo las mismas.')),
        (t('3. Canali','3. Canales'), t('Voce in tempo reale e WhatsApp, con lo stesso agente. WhatsApp Business gestito da Odyra: numeri, template e conversazioni, con la titolarità dell\'account al cliente.','Voz en tiempo real y WhatsApp, con el mismo agente. WhatsApp Business gestionado por Odyra: números, plantillas y conversaciones, con la titularidad de la cuenta en el cliente.')),
        (t('4. Gestione operativa','4. Gestión operativa'), t('Un agente per ogni cliente, con dati e configurazione isolati. Limiti e avvisi di consumo, controllo di qualità automatico, monitoraggio degli errori con diagnosi, riassunti per il titolare, passaggio a una persona.','Un agente para cada cliente, con datos y configuración aislados. Límites y avisos de consumo, control de calidad automático, monitorización de errores con diagnóstico, resúmenes para el titular, paso a una persona.')),
        (t('5. Conformità','5. Cumplimiento'), t('L\'agente dice sempre di essere un\'AI, i dati sono separati per ogni azienda, il trattamento è conforme al GDPR e progettato nel perimetro dell\'AI Act. Supporto alla documentazione per i partner in settori regolati.','El agente dice siempre que es una IA, los datos están separados para cada empresa, el tratamiento es conforme al RGPD y está diseñado dentro del perímetro del AI Act. Apoyo a la documentación para socios en sectores regulados.')),
    ]))
    body += sec(f'''{sec_h(t('Come nasce un nuovo cliente.','Cómo nace un nuevo cliente.'), t('Dal momento in cui il software di gestione è collegato.','Desde el momento en que el software de gestión está conectado.'))}{steps([
        (t('Si crea il cliente','Se crea el cliente'), t('Un solo passaggio crea l\'azienda con i suoi limiti e le sue impostazioni, senza duplicati.','Un solo paso crea la empresa con sus límites y sus ajustes, sin duplicados.')),
        (t('Staff e listino arrivano da soli','Equipo y tarifas llegan solos'), t('Si sincronizzano dal software di gestione ogni notte; la base di conoscenza dell\'agente si aggiorna con loro.','Se sincronizan desde el software de gestión cada noche; la base de conocimiento del agente se actualiza con ellos.')),
        (t('Lo specialista attiva i canali','El especialista activa los canales'), t('Numero, WhatsApp e voce: una procedura di circa dieci minuti.','Número, WhatsApp y voz: un procedimiento de unos diez minutos.')),
    ])}''', 'sec-alt')
    body += sec(f'''<div class="split"><div><h2>{t('WhatsApp Business ufficiale.','WhatsApp Business oficial.')}</h2></div><div><p class="lead">{t('Odyra è Tech Provider Meta tramite Vonage: gestiamo l\'infrastruttura di numeri e template per tutti i clienti, su più account WhatsApp Business.','Odyra es Tech Provider de Meta a través de Vonage: gestionamos la infraestructura de números y plantillas para todos los clientes, sobre varias cuentas de WhatsApp Business.')}</p>
      <div class="logos" style="margin-top:28px"><img src="/assets/logos/whatsapp.svg" alt="WhatsApp" style="height:46px"><img src="/assets/logos/meta.svg" alt="Meta" style="height:30px"><img src="/assets/logos/vonage.svg" alt="Vonage" style="height:30px"></div>
      <p style="margin-top:20px;font-size:.88rem;color:var(--muted)">{t('WhatsApp e Meta sono marchi di Meta Platforms, Inc.; Vonage è un marchio di Vonage Holdings Corp. Odyra non è affiliata a tali società.','WhatsApp y Meta son marcas de Meta Platforms, Inc.; Vonage es una marca de Vonage Holdings Corp. Odyra no está afiliada a dichas empresas.')}</p></div></div>''')
    body += cta(t('Domande tecniche o di conformità?','¿Preguntas técnicas o de cumplimiento?'), t('Rispondiamo ai tuoi referenti IT e legali.','Atendemos a tus responsables de TI y legal.'))
    return layout('piattaforma', t('La piattaforma — Odyra System', 'La plataforma — Odyra System'), t('Cinque strati: regole di settore, connettori, canali, gestione operativa, conformità. La piattaforma proprietaria di Odyra.', 'Cinco capas: reglas de sector, conectores, canales, gestión operativa, cumplimiento. La plataforma propia de Odyra.'), body)

# ───────── SETTORI ─────────
def page_settori():
    body = head_(t('Settori di competenza.','Sectores de competencia.'),
        t('Prima di costruire un agente impariamo il settore a fondo: ogni regola, ogni abitudine, ogni caso limite.','Antes de construir un agente aprendemos el sector a fondo: cada regla, cada costumbre, cada caso límite.'))
    body += sec(f'{sec_h(t("Come entriamo in un settore.","Cómo entramos en un sector."))}' + steps([
        (t('Ascoltiamo','Escuchamos'), t('Come lavora chi fa quel lavoro, cosa chiedono i clienti, dove si perdono chiamate e tempo.','Cómo trabaja quien hace ese trabajo, qué piden los clientes, dónde se pierden llamadas y tiempo.')),
        (t('Codifichiamo le regole','Codificamos las reglas'), t('Ogni regola del settore diventa codice: l\'agente la rispetta sempre.','Cada regla del sector se convierte en código: el agente la respeta siempre.')),
        (t('Ci colleghiamo','Nos conectamos'), t('Ai software di gestione che quel settore usa già.','A los software de gestión que ese sector ya usa.')),
        (t('Gestiamo e misuriamo','Gestionamos y medimos'), t('Qualità, consumi e risultati, per migliorare ogni settimana.','Calidad, consumos y resultados, para mejorar cada semana.')),
    ]))
    body += sec(f'''{sec_h(t('Beauty.','Beauty.'), t('Il settore in cui siamo primi: parrucchieri e centri estetici.','El sector en el que somos los primeros: peluquerías y centros de estética.'))}
      <div class="split"><div><img class="boss-logo" src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers"><p class="lead">{t('Con BOSS e il suo software GoWeb, l\'agente è oggi disponibile per la rete di oltre 1.500 saloni, col nome GoAgent.','Con BOSS y su software GoWeb, el agente está hoy disponible para la red de más de 1.500 salones, con el nombre GoAgent.')}</p>
      <div class="btns"><a class="btn btn-p" href="{url('goagent')}">{t('Scopri GoAgent','Descubre GoAgent')}</a></div></div>
      <div>{beauty_rules(8)}</div></div>''', 'sec-alt')
    body += sec(f'''{sec_h(t('Una piattaforma, tanti settori.','Una plataforma, muchos sectores.'), t('Stessa piattaforma, regole diverse per ogni settore.','Misma plataforma, reglas distintas para cada sector.'))}{verts()}''')
    body += cta(t('Hai un software di gestione?','¿Tienes un software de gestión?'), t('Raccontacelo: vediamo insieme come portare l\'agente ai tuoi clienti.','Cuéntanoslo: vemos juntos cómo llevar el agente a tus clientes.'), 'partner')
    return layout('settori', t('Settori di competenza — Odyra System', 'Sectores de competencia — Odyra System'), t('Settori di competenza: beauty con BOSS e GoAgent, dentale, autofficine, ospitalità, veterinari e altri.', 'Sectores de competencia: beauty con BOSS y GoAgent, dental, talleres, hostelería, veterinarios y otros.'), body)

# ───────── PARTNER ─────────
def page_partner():
    body = head_(t('Un\'AI di settore per i tuoi clienti. Col tuo marchio.','Una IA sectorial para tus clientes. Con tu marca.'),
        t('Il tuo software di gestione offre un agente che risponde, prenota e organizza al posto del cliente. Tu porti i clienti, Odyra porta prodotto, tecnologia e gestione.','Tu software de gestión ofrece un agente que responde, reserva y organiza en lugar del cliente. Tú aportas los clientes, Odyra aporta producto, tecnología y gestión.'),
        f'<a class="btn btn-p" href="{url("contatti")}?interesse=partner">{t("Diventa partner","Hazte socio")}</a>')
    body += sec(f'''{sec_h(t('Cosa fai tu. Cosa facciamo noi.','Qué haces tú. Qué hacemos nosotros.'))}<div class="split split-e"><div>{rows([
        (t('Tu','Tú'), t('Offri il servizio ai tuoi clienti col tuo marchio. Ci dai accesso alle API: ricerca cliente, disponibilità, creazione e cancellazione appuntamenti.','Ofreces el servicio a tus clientes con tu marca. Nos das acceso a las API: búsqueda de cliente, disponibilidad, creación y cancelación de citas.')),
        (t('Il tuo guadagno','Tu ganancia'), t('Un nuovo canone ricorrente da ogni cliente che attiva l\'agente, con revenue condivisa con Odyra.','Una nueva cuota recurrente de cada cliente que activa el agente, con revenue compartida con Odyra.')),
      ])}</div><div>{rows([
        (t('Odyra','Odyra'), t('Agente di settore, connettore col tuo software, onboarding dei clienti, dashboard per i titolari, WhatsApp Business, controlli di qualità e assistenza.','Agente sectorial, conector con tu software, onboarding de clientes, panel para los titulares, WhatsApp Business, controles de calidad y asistencia.')),
        (t('Il tuo marchio','Tu marca'), t('Interfacce, messaggi e dashboard portano il tuo logo.','Interfaces, mensajes y paneles llevan tu logo.')),
      ])}</div></div>''')
    body += sec(f'''{sec_h(t('Come si parte.','Cómo se empieza.'))}{steps([
        (t('Collegamento','Conexión'), t('Un connettore dedicato collega il tuo software alla piattaforma, senza toccarne il cuore.','Un conector dedicado conecta tu software con la plataforma, sin tocar su núcleo.')),
        (t('Attivazione dei clienti','Activación de clientes'), t('Staff e listino si sincronizzano da soli. Numero, WhatsApp e voce li configura uno specialista Odyra, in circa dieci minuti.','Equipo y tarifas se sincronizan solos. Número, WhatsApp y voz los configura un especialista de Odyra, en unos diez minutos.')),
        (t('Gestione continua','Gestión continua'), t('Controlliamo qualità, errori e consumi. Il cliente vede tutto nella sua dashboard.','Controlamos calidad, errores y consumos. El cliente lo ve todo en su panel.')),
    ])}''', 'sec-alt')
    body += sec(f'<div class="split"><div>{vid("partner-program")}</div><div><h2>{t("Il programma partner, spiegato.","El programa de socios, explicado.")}</h2><p class="lead" style="margin-top:18px">{t("Un video di pochi minuti: cosa include, come funziona e cosa ricevi.","Un vídeo de pocos minutos: qué incluye, cómo funciona y qué recibes.")}</p></div></div>')
    body += sec(f'''{sec_h(t('Un caso reale.','Un caso real.'))}<div class="split"><div><img class="boss-logo" src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers"></div>
      <div><p class="lead">{t('BOSS sviluppa GoWeb, tra i software più diffusi per parrucchieri e centri estetici in Italia, con oltre 1.500 saloni. Con Odyra ha lanciato GoAgent col proprio marchio.','BOSS desarrolla GoWeb, uno de los software más extendidos entre peluquerías y centros de estética en Italia, con más de 1.500 salones. Con Odyra lanzó GoAgent con su marca.')}</p>
      <div class="btns"><a class="btn btn-o" href="{url('goagent')}">{t('La storia di GoAgent','La historia de GoAgent')}</a></div></div></div>''')
    body += sec(f'''{sec_h(t('Settori di competenza.','Sectores de competencia.'))}{verts()}''', 'sec-alt')
    body += cta(t('Porta l\'AI nel tuo software di gestione.','Lleva la IA a tu software de gestión.'), t('Parliamo di integrazione, formula e tempi.','Hablemos de integración, fórmula y plazos.'), 'partner', t('Diventa partner','Hazte socio'))
    return layout('partner', t('Per i partner — AI di settore in white-label · Odyra System', 'Para socios — IA sectorial en white-label · Odyra System'), t('Il tuo software di gestione offre un agente AI di settore ai suoi clienti, col tuo marchio. Odyra porta prodotto, tecnologia e gestione.', 'Tu software de gestión ofrece un agente IA sectorial a sus clientes, con tu marca. Odyra aporta producto, tecnología y gestión.'), body)

# ───────── GOAGENT (identità propria: viola e giallo) ─────────
def dash_gallery():
    shots = [('panoramica', t('Panoramica: chiamate, appuntamenti fissati dall\'AI, conversione, ore risparmiate.','Resumen: llamadas, citas fijadas por la IA, conversión, horas ahorradas.')),
             ('inbox-whatsapp', t('Inbox WhatsApp: il titolare può prendere in carico la conversazione e restituirla all\'AI.','Bandeja de WhatsApp: el titular puede asumir la conversación y devolverla a la IA.')),
             ('chiamate', t('Chiamate: trascrizione, riassunto e dettagli dell\'appuntamento.','Llamadas: transcripción, resumen y detalles de la cita.')),
             ('pacchetti', t('Pacchetti: servizi abbinati con prezzo e durata totali.','Paquetes: servicios combinados con precio y duración totales.')),
             ('consumi', t('Consumi del piano e impostazioni dell\'agente.','Consumos del plan y ajustes del agente.'))]
    out = ''
    for n, cap in shots:
        if os.path.exists(os.path.join(ROOT, f'assets/goagent/{n}.png')):
            out += f'<figure><img src="/assets/goagent/{n}.png" alt="{e(cap)}"><figcaption>{cap}</figcaption></figure>'
    return f'<div class="gallery">{out}</div><p class="vid-cap">{t("Schermate della dashboard GoAgent con dati di prova.","Capturas del panel GoAgent con datos de prueba.")}</p>' if out else ''

def page_goagent():
    body = f'''<section class="ga-hero"><div class="wrap ga-grid">
  <div>
    <p class="ga-kicker">{t('Il servizio AI di BOSS per i saloni GoWeb','El servicio IA de BOSS para los salones GoWeb')}</p>
    <h1>GoAgent AI Concierge</h1>
    <p class="lead">{t('Risponde al telefono e su WhatsApp, giorno e notte, e prenota direttamente nell\'agenda del salone. Parla come un salone, conosce il mestiere, lavora dentro GoWeb.','Responde al teléfono y por WhatsApp, de día y de noche, y reserva directamente en la agenda del salón. Habla como un salón, conoce el oficio, trabaja dentro de GoWeb.')}</p>
    <div class="btns"><a class="btn btn-p" href="{LINK_BOSS}" rel="noopener">{t('Vai a BOSS','Ir a BOSS')} ↗</a><a class="btn btn-o" href="#video">{t('Guarda il video','Mira el vídeo')}</a></div>
  </div>
  <div class="ga-badge"><img class="bl" src="/assets/logos/boss-my-numbers.png" alt="Boss My Numbers"><p>{t('GoAgent è un servizio di BOSS. Sviluppato e gestito da Odyra System.','GoAgent es un servicio de BOSS. Desarrollado y gestionado por Odyra System.')}</p></div>
</div></section>

<section class="sec" id="video"><div class="wrap">{sec_h(t('Che cos\'è GoAgent.','Qué es GoAgent.'), '', True)}<div class="vid-wide">{vid('goagent', t('Il video di presentazione di GoAgent.','El vídeo de presentación de GoAgent.'))}</div></div></section>

<section class="sec sec-alt" id="storia"><div class="wrap">
  {sec_h(t('La storia.','La historia.'))}
  {steps([
    (t('Il problema','El problema'), t('I saloni perdono prenotazioni ogni giorno: il telefono squilla mentre lo staff lavora, i messaggi arrivano a negozio chiuso.','Los salones pierden reservas cada día: el teléfono suena mientras el equipo trabaja, los mensajes llegan con el local cerrado.')),
    (t('La scelta di BOSS','La decisión de BOSS'), t('BOSS sviluppa GoWeb, con oltre 1.500 saloni. Voleva offrire ai suoi clienti un assistente AI vero, integrato nel gestionale, senza costruirlo in casa.','BOSS desarrolla GoWeb, con más de 1.500 salones. Quería ofrecer a sus clientes un asistente IA real, integrado en el software, sin construirlo en casa.')),
    (t('Il lancio','El lanzamiento'), t('Odyra ha costruito GoAgent: l\'agente, l\'onboarding dei saloni, la dashboard e la gestione. In produzione da giugno 2026.','Odyra construyó GoAgent: el agente, el onboarding de los salones, el panel y la gestión. En producción desde junio de 2026.')),
  ])}
  <div class="news"><b>17-19 {t('ottobre','octubre')}</b><span>{t('BOSS inaugura GoAgent alla sua convention, con oltre 300 persone.','BOSS inaugura GoAgent en su convención, con más de 300 personas.')}</span></div>
</div></section>

<section class="sec" id="funzioni"><div class="wrap">
  {sec_h(t('Conosce il mestiere.','Conoce el oficio.'), t('Le regole del salone sono nel codice, non solo in un prompt. Qui ne vedi una parte: ce ne sono molte di più.','Las reglas del salón están en el código, no solo en un prompt. Aquí ves una parte: hay muchas más.'))}
  {beauty_rules()}
</div></section>

<section class="sec sec-alt"><div class="wrap split">
  <div><h2>{t('Voce e WhatsApp.','Voz y WhatsApp.')}</h2></div>
  <div>{rows([
    (t('Un solo agente','Un solo agente'), t('Risponde al telefono e su WhatsApp, 24 ore su 24, anche su più conversazioni insieme.','Responde al teléfono y por WhatsApp, las 24 horas, también en varias conversaciones a la vez.')),
    (t('Dentro GoWeb','Dentro de GoWeb'), t('Legge servizi, operatori, turni e disponibilità e scrive gli appuntamenti nell\'agenda.','Lee servicios, profesionales, turnos y disponibilidad y escribe las citas en la agenda.')),
    (t('Parla come un salone','Habla como un salón'), t('Frasi brevi, una domanda alla volta, il nome della cliente e la sua ultima visita. Dice sempre di essere un\'assistente AI.','Frases cortas, una pregunta a la vez, el nombre de la clienta y su última visita. Dice siempre que es una asistente IA.')),
    (t('Conferme su WhatsApp','Confirmaciones por WhatsApp'), t('Conferma e disdetta di ogni appuntamento, con messaggi approvati.','Confirmación y cancelación de cada cita, con mensajes aprobados.')),
  ])}</div>
</div></section>

<section class="sec" id="dashboard"><div class="wrap">
  {sec_h(t('La dashboard del titolare.','El panel del titular.'), t('Panoramica, inbox WhatsApp con presa in carico, chiamate, pacchetti e consumi del piano.','Resumen, bandeja de WhatsApp con asunción de la conversación, llamadas, paquetes y consumos del plan.'))}
  {dash_gallery()}
</div></section>

<section class="sec sec-alt"><div class="wrap split">
  <div><h2>{t('In arrivo.','Próximamente.')}</h2></div>
  <div><p class="lead">{t('Chiamate in uscita ai clienti che non tornano in salone: l\'agente li richiama, al telefono o su WhatsApp, e li riporta in agenda.','Llamadas salientes a los clientes que no vuelven al salón: el agente los vuelve a llamar, por teléfono o WhatsApp, y los devuelve a la agenda.')}</p>
  <div class="btns"><a class="btn btn-p" href="{LINK_BOSS}" rel="noopener">{t('Scopri GoAgent su BOSS','Descubre GoAgent en BOSS')} ↗</a></div></div>
</div></section>'''
    return layout('goagent', t('GoAgent AI Concierge — BOSS · sviluppato da Odyra', 'GoAgent AI Concierge — BOSS · desarrollado por Odyra'), t('GoAgent è il servizio AI di BOSS per i saloni GoWeb: risponde al telefono e su WhatsApp e prenota nell\'agenda. Sviluppato e gestito da Odyra.', 'GoAgent es el servicio IA de BOSS para los salones GoWeb: responde al teléfono y por WhatsApp y reserva en la agenda. Desarrollado y gestionado por Odyra.'), body, goagent=True)

# ───────── SU MISURA ─────────
def page_custom():
    body = head_(t('Progetti su misura per aziende con grandi volumi.','Proyectos a medida para empresas con grandes volúmenes.'),
        t('La stessa piattaforma, applicata ai processi di una singola azienda: vendite, customer service e back office, integrati con CRM ed ERP.','La misma plataforma, aplicada a los procesos de una sola empresa: ventas, atención al cliente y back office, integrados con CRM y ERP.'),
        f'<a class="btn btn-p" href="{url("contatti")}?interesse=custom">{t("Parliamo del progetto","Hablemos del proyecto")}</a>')
    body += sec(f'''{sec_h(t('Dove l\'AI fa lavoro vero.','Donde la IA hace trabajo real.'))}{rows([
        (t('Vendite','Ventas'), t('Un agente richiama ogni lead in pochi secondi, lo qualifica con domande strutturate e fissa l\'appuntamento nel calendario del team. Chi non risponde al telefono viene recuperato su WhatsApp.','Un agente llama a cada lead en pocos segundos, lo califica con preguntas estructuradas y fija la cita en el calendario del equipo. Quien no contesta al teléfono se recupera por WhatsApp.')),
        (t('Customer service','Atención al cliente'), t('Voce, WhatsApp ed e-mail, con risposte coerenti e passaggio a una persona quando serve.','Voz, WhatsApp y e-mail, con respuestas coherentes y paso a una persona cuando hace falta.')),
        (t('Back office','Back office'), t('Automazioni sui processi ripetitivi, tra i sistemi che l\'azienda usa già.','Automatizaciones en procesos repetitivos, entre los sistemas que la empresa ya usa.')),
    ])}''')
    body += sec(f'''<div class="split"><div><span class="tile"><img src="/assets/logos/sportit.png" alt="Sportit.com"></span><h2 style="margin-top:32px">Gruppo Colzani.</h2></div>
      <div><p class="lead">{t('Gruppo Colzani, dietro Sportit.com e Global Trading, genera centinaia di lead a ogni campagna. L\'agente commerciale di Odyra scrive subito su WhatsApp, richiama in pochi secondi, qualifica e fissa l\'appuntamento, e scrive l\'esito nel CRM. La collaborazione prosegue con l\'automazione del customer service e-mail per i marketplace.','Gruppo Colzani, detrás de Sportit.com y Global Trading, genera cientos de leads en cada campaña. El agente comercial de Odyra escribe enseguida por WhatsApp, llama en pocos segundos, califica y fija la cita, y escribe el resultado en el CRM. La colaboración continúa con la automatización de la atención por e-mail para marketplaces.')}</p></div></div>''', 'sec-alt')
    body += sec(f'''{sec_h(t('Come lavoriamo.','Cómo trabajamos.'))}{steps([
        (t('Capiamo il processo','Entendemos el proceso'), t('Dove si perdono chiamate, tempo e margine.','Dónde se pierden llamadas, tiempo y margen.')),
        (t('Disegniamo e integriamo','Diseñamos e integramos'), t('Cosa sa l\'agente, quando passa la mano a una persona, con quali sistemi si collega.','Qué sabe el agente, cuándo cede el paso a una persona, con qué sistemas se conecta.')),
        (t('Misuriamo','Medimos'), t('Chiamate, esiti e tempi in una dashboard, per migliorare ogni settimana.','Llamadas, resultados y tiempos en un panel, para mejorar cada semana.')),
    ])}''')
    body += cta(t('Hai un processo da automatizzare?','¿Tienes un proceso que automatizar?'), t('Raccontacelo: ti diciamo cosa si può fare e in quanto tempo.','Cuéntanoslo: te decimos qué se puede hacer y en cuánto tiempo.'), 'custom')
    return layout('custom', t('Progetti su misura — Odyra System', 'Proyectos a medida — Odyra System'), t('Agenti e automazioni AI su misura per vendite, customer service e back office, integrati con CRM ed ERP. Caso: Gruppo Colzani.', 'Agentes y automatizaciones IA a medida para ventas, atención al cliente y back office, integrados con CRM y ERP. Caso: Gruppo Colzani.'), body)

# ───────── IL GRUPPO ─────────
def page_gruppo():
    body = head_(t('Un metodo: un settore alla volta.','Un método: un sector a la vez.'),
        t('Odyra è un gruppo tecnologico milanese. Impariamo un settore a fondo e costruiamo il software con l\'AI che lo fa. Lo portiamo ai clienti in due modi.','Odyra es un grupo tecnológico milanés. Aprendemos un sector a fondo y construimos el software con IA que lo hace. Lo llevamos a los clientes de dos maneras.'))
    body += sec(rows([
        (t('Con i software di gestione','Con los software de gestión'), t('Agenti di settore in white-label dentro il software che i clienti usano già. Beauty, con GoAgent di BOSS.','Agentes sectoriales en white-label dentro del software que los clientes ya usan. Beauty, con GoAgent de BOSS.'), url('partner')),
        (t('In proprio','Por cuenta propia'), t('Software proprietari venduti direttamente. HAKO, per le portinerie dei condomini, e altri in arrivo.','Software propio vendido directamente. HAKO, para las conserjerías de las comunidades, y otros en camino.'), LINK_HAKO),
        (t('Su misura','A medida'), t('Agenti e automazioni per aziende con grandi volumi.','Agentes y automatizaciones para empresas con grandes volúmenes.'), url('custom')),
    ]))
    body += sec(f'''{sec_h(t('Missione e visione.','Misión y visión.'))}{rows([
        (t('Missione','Misión'), t('Dare a ogni azienda, dal singolo salone al gruppo industriale, una forza di lavoro AI affidabile, integrata e misurabile.','Dar a cada empresa, del salón individual al grupo industrial, una fuerza de trabajo de IA fiable, integrada y medible.')),
        (t('Visione','Visión'), t('Diventare il gruppo europeo di riferimento per i software AI verticali: prodotti proprietari, ciascuno leader nel proprio mercato, su un\'unica infrastruttura condivisa.','Convertirnos en el grupo europeo de referencia del software de IA vertical: productos propios, cada uno líder en su mercado, sobre una única infraestructura compartida.')),
    ])}''', 'sec-alt')
    body += sec(f'<table><tr><th>{t("Società","Sociedad")}</th><td>Verypos S.r.l.</td></tr><tr><th>{t("Sede","Sede")}</th><td>Viale Papiniano 8, 20123 Milano</td></tr><tr><th>{t("Contatto","Contacto")}</th><td><a class="link" href="mailto:{EMAIL}">{EMAIL}</a></td></tr></table>')
    body += cta(t('Lavoriamo insieme.','Trabajemos juntos.'), t('Che tu sia un software di gestione o un\'azienda, raccontaci il tuo caso.','Seas un software de gestión o una empresa, cuéntanos tu caso.'))
    return layout('gruppo', t('Il gruppo — Odyra System', 'El grupo — Odyra System'), t('Odyra impara un settore alla volta e costruisce il software con l\'AI che lo fa: con i software di gestione, in proprio e su misura.', 'Odyra aprende un sector a la vez y construye el software con IA que lo hace: con software de gestión, por cuenta propia y a medida.'), body)

# ───────── CONTATTI / PRIVACY / 404 ─────────
def page_contatti():
    opts = [('partner', t('Partnership per software di gestione','Alianza para software de gestión')), ('goagent', 'GoAgent'), ('hako', 'HAKO'), ('custom', t('Progetto su misura','Proyecto a medida')), ('altro', t('Altro','Otro'))]
    oh = ''.join(f'<option value="{v}">{e(n)}</option>' for v, n in opts)
    body = head_(t('Parliamo del tuo caso.','Hablemos de tu caso.'), t('Raccontaci come lavori oggi. Ti rispondiamo entro un giorno lavorativo.','Cuéntanos cómo trabajas hoy. Te respondemos en un día laborable.'))
    body += sec(f'''<div class="split split-e"><form class="form" id="form-contatti" novalidate>
    <div class="row"><label>{t('Nome e cognome','Nombre y apellidos')}<input name="nome" required autocomplete="name"></label><label>{t('Azienda','Empresa')}<input name="azienda" required autocomplete="organization"></label></div>
    <div class="row"><label>E-mail<input type="email" name="email" required autocomplete="email"></label><label>{t('Telefono','Teléfono')}<input type="tel" name="telefono" autocomplete="tel"></label></div>
    <label>{t('Di cosa hai bisogno?','¿Qué necesitas?')}<select name="interesse" required>{oh}</select></label>
    <label>{t('Messaggio','Mensaje')}<textarea name="messaggio" placeholder="{t('Che software di gestione sviluppate? Quanti clienti avete?','¿Qué software de gestión desarrolláis? ¿Cuántos clientes tenéis?')}"></textarea></label>
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

BUILDERS = {'home': page_home, 'piattaforma': page_piattaforma, 'settori': page_settori, 'partner': page_partner, 'goagent': page_goagent, 'custom': page_custom, 'gruppo': page_gruppo, 'contatti': page_contatti}

def write(rel, content):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    global L
    # pulizia delle pagine generate in passato
    for old in ('hako.html', 'tecnologia.html', 'es/hako.html', 'es/tecnologia.html'):
        p = os.path.join(ROOT, old)
        if os.path.exists(p):
            os.remove(p)
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
