#!/usr/bin/env python3
"""Genera il sito Odyra System in dist/ (italiano in radice, spagnolo in /es/).

Uso: python3 build.py

Da un'unica fonte escono, per ogni pagina: HTML statico, versione Markdown (/pagina.md),
dati strutturati JSON-LD. Per tutto il sito: llms.txt, llms-full.txt, sitemap.xml, robots.txt.
Solo libreria standard di Python.
"""
import html
import json
import os
import re
import shutil
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(ROOT, 'static')
DIST = os.path.join(ROOT, 'dist')

SITE = 'https://odyrasystemautomation.it'
EMAIL = 'team@odyrasystemautomation.it'
UPDATED = '2026-10-20'  # data dell'ultimo aggiornamento dei contenuti (sitemap, JSON-LD)
LINK_HAKO = 'https://hakocondomini.com'
LINK_BOSS = 'https://bossitalia.com'
COMPANY = {
    'legal': 'Verypos S.r.l.',
    'vat': '11630390968',
    'rea': 'MI-2615892',
    'street': 'Viale Papiniano 8',
    'zip': '20123',
    'city': 'Milano',
}
LANGS = ('it', 'es')
L = 'it'


def t(it, es):
    return it if L == 'it' else es


def e(s):
    return html.escape(s, quote=True)


# ───────── pagine e indirizzi ─────────
# chiave: (percorso it, percorso es)
PATHS = {
    'home': ('', ''),
    'piattaforma': ('piattaforma', 'plataforma'),
    'settori': ('settori', 'sectores'),
    'partner': ('partner', 'socios'),
    'goagent': ('goagent', 'goagent'),
    'misura': ('su-misura', 'a-medida'),
    'chi': ('chi-siamo', 'quienes-somos'),
    'faq': ('domande', 'preguntas'),
    'contatti': ('contatti', 'contacto'),
    'privacy': ('privacy', 'privacidad'),
}


def url(key, lang=None):
    lang = lang or L
    p = PATHS[key][LANGS.index(lang)]
    base = '/' if lang == 'it' else '/es/'
    return base + (p + '/' if p else '')


def md_url(key, lang=None):
    lang = lang or L
    p = PATHS[key][LANGS.index(lang)]
    base = '/' if lang == 'it' else '/es/'
    return base + (p or 'index') + '.md'


def nav_items():
    return [
        ('piattaforma', t('Piattaforma', 'Plataforma')),
        ('settori', t('Settori', 'Sectores')),
        ('partner', t('Per i software', 'Para software')),
        ('goagent', 'GoAgent'),
        ('misura', t('Su misura', 'A medida')),
        ('chi', t('Chi siamo', 'Quiénes somos')),
    ]


# ───────── componenti ─────────
def btn(href, label, kind='p', extra=''):
    return f'<a class="btn btn-{kind}" href="{href}"{extra}>{label}</a>'


def head_block(h1, lead, buttons=''):
    return f'''<section class="phead"><div class="wrap">
  <h1>{h1}</h1>
  <p class="lead">{lead}</p>
  {f'<p class="btns">{buttons}</p>' if buttons else ''}
</div></section>'''


def section(h2, inner, intro='', cls='', sid=''):
    ida = f' id="{sid}"' if sid else ''
    return f'''<section class="sec {cls}"{ida}><div class="wrap">
  <header class="sec-h"><h2>{h2}</h2>{f'<p>{intro}</p>' if intro else ''}</header>
  {inner}
</div></section>'''


def steps(items):
    return '<ol class="steps">' + ''.join(f'<li><h3>{a}</h3><p>{b}</p></li>' for a, b in items) + '</ol>'


def points(items, cls='points'):
    return f'<ul class="{cls}">' + ''.join(f'<li><h3>{a}</h3><p>{b}</p></li>' for a, b in items) + '</ul>'


def facts(items):
    return '<dl class="facts">' + ''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a, b in items) + '</dl>'


def cta(h2=None, p=None, label=None, interest=''):
    h2 = h2 or t('Parliamo del tuo software.', 'Hablemos de tu software.')
    p = p or t('Ti mostriamo l’agente al lavoro, con tempi di integrazione e formula commerciale.',
               'Te mostramos el agente trabajando, con plazos de integración y fórmula comercial.')
    q = f'?interesse={interest}' if interest else ''
    return f'''<section class="cta"><div class="wrap">
  <div><h2>{h2}</h2><p>{p}</p></div>
  <p class="btns">{btn(url('contatti') + q, label or t('Richiedi una demo', 'Solicita una demo'), 'w')}</p>
</div></section>'''


def faq_list(items):
    return '<div class="faq">' + ''.join(
        f'<details><summary><h3>{q}</h3></summary><div class="ans"><p>{a}</p></div></details>' for q, a in items) + '</div>'


def video(name, title, desc):
    """Inserisce il video solo se il file esiste in static/assets/video/. Niente segnaposto vuoti."""
    base = os.path.join(STATIC, 'assets', 'video', name)
    if not os.path.exists(base + '.mp4'):
        return '', None
    poster = f' poster="/assets/video/{name}.jpg"' if os.path.exists(base + '.jpg') else ''
    tracks = ''
    for lg, label in (('it', 'Italiano'), ('es', 'Español'), ('en', 'English'), ('de', 'Deutsch'), ('fr', 'Français')):
        if os.path.exists(f'{base}.{lg}.vtt'):
            d = ' default' if lg == L and lg != 'it' else ''
            tracks += f'<track kind="subtitles" srclang="{lg}" label="{label}" src="/assets/video/{name}.{lg}.vtt"{d}>'
    tag = f'<figure class="video"><video controls playsinline preload="metadata"{poster} src="/assets/video/{name}.mp4">{tracks}</video><figcaption>{desc}</figcaption></figure>'
    ld = {'@type': 'VideoObject', 'name': title, 'description': desc, 'contentUrl': f'{SITE}/assets/video/{name}.mp4',
          'uploadDate': UPDATED, 'thumbnailUrl': f'{SITE}/assets/video/{name}.jpg' if poster else f'{SITE}/assets/img/og.jpg'}
    return tag, ld


def salon_rules(n=None):
    r = [
        (t('Riconosce la cliente dal numero', 'Reconoce a la clienta por el número'),
         t('e sa cosa ha fatto di recente. Se due clienti usano lo stesso numero, chiede chi sta parlando.',
           'y sabe qué se hizo últimamente. Si dos clientas usan el mismo número, pregunta quién habla.')),
        (t('Prenota più servizi in una sola visita', 'Reserva varios servicios en una sola visita'),
         t('cercando un unico slot, senza buchi tra un servizio e l’altro.',
           'buscando un único hueco, sin vacíos entre un servicio y otro.')),
        (t('Rispetta l’ordine tecnico', 'Respeta el orden técnico'),
         t('colore, taglio, piega; schiaritura, tonalizzante, piega. L’ordine lo impone il sistema.',
           'color, corte, peinado; decoloración, matiz, peinado. El orden lo impone el sistema.')),
        (t('Aggiunge la piega finale', 'Añade el peinado final'),
         t('dopo colore, taglio donna e trattamenti, quando serve. Per l’uomo non la propone.',
           'tras color, corte de mujer y tratamientos, cuando hace falta. A los hombres no se lo propone.')),
        (t('Gestisce i pacchetti', 'Gestiona los paquetes'),
         t('un servizio ne porta con sé altri, con operatore e ordine fissi, e dice sempre prezzo e durata del totale.',
           'un servicio arrastra otros, con profesional y orden fijos, y dice siempre precio y duración del total.')),
        (t('Inserisce la consulenza', 'Inserta la consulta'),
         t('quando il servizio la richiede, in testa alla sequenza.', 'cuando el servicio la exige, al inicio de la secuencia.')),
        (t('Rispetta la scelta dell’operatore', 'Respeta la elección del profesional'),
         t('segue la preferenza della cliente; con “staff riservato” il salone sceglie di non far prenotare per nome.',
           'sigue la preferencia de la clienta; con “equipo reservado” el salón decide no reservar por nombre.')),
        (t('Capisce le fasce orarie', 'Entiende las franjas horarias'),
         t('“mattina”, “pomeriggio”, “dopo le 17”, e confronta più giorni nello stesso messaggio.',
           '“mañana”, “tarde”, “después de las 17”, y compara varios días en el mismo mensaje.')),
        (t('Prenota solo orari reali', 'Reserva solo horarios reales'),
         t('e scrive “prenotato” solo dopo la conferma del gestionale.', 'y escribe “reservado” solo tras la confirmación del software de gestión.')),
        (t('Sposta senza creare doppioni', 'Cambia citas sin duplicados'),
         t('prima prenota il nuovo appuntamento, poi cancella il vecchio.', 'primero reserva la cita nueva, luego cancela la antigua.')),
        (t('Applica la regola delle 24 ore', 'Aplica la regla de las 24 horas'),
         t('nelle 24 ore prima dell’appuntamento la disdetta passa al salone.', 'en las 24 horas previas a la cita, la cancelación pasa al salón.')),
        (t('Avvisa il salone', 'Avisa al salón'),
         t('quando la cliente è in ritardo, sta arrivando o è fuori.', 'cuando la clienta llega tarde, está llegando o espera fuera.')),
        (t('Passa la conversazione a una persona', 'Pasa la conversación a una persona'),
         t('quando serve, anche durante la chiamata: l’operatore entra nella stessa conversazione.',
           'cuando hace falta, incluso durante la llamada: la persona entra en la misma conversación.')),
        (t('Dice sempre di essere un’AI', 'Dice siempre que es una IA'),
         t('al telefono e su WhatsApp, come richiede l’AI Act.', 'por teléfono y por WhatsApp, como exige el AI Act.')),
        (t('Segue le regole del salone', 'Sigue las reglas del salón'),
         t('clientela riservata, prezzi nascosti, chiusure straordinarie e ferie.', 'clientela reservada, precios ocultos, cierres extraordinarios y vacaciones.')),
    ]
    r = r[:n] if n else r
    return '<ul class="rules">' + ''.join(f'<li><b>{a}</b> {b}</li>' for a, b in r) + '</ul>'


def transcript():
    """Conversazione di esempio con le regole annotate a margine: il pezzo che racconta Odyra a colpo d'occhio."""
    msgs = [
        ('c', t('Cliente', 'Clienta'), t('Ciao! Sabato mattina riuscite a farmi colore e taglio?', '¡Hola! ¿El sábado por la mañana me podéis hacer color y corte?'), None),
        ('a', t('Agente', 'Agente'), t('Ciao Giulia, sono l’assistente AI del salone. Sabato alle 9:30 c’è posto con Marta: colore, taglio e piega finale, 2 ore e 15 in tutto, 92 €. Ti va bene?',
                                       'Hola, Giulia, soy el asistente IA del salón. El sábado a las 9:30 hay hueco con Marta: color, corte y peinado final, 2 horas y 15 en total, 92 €. ¿Te va bien?'),
         [t('Riconosce la cliente dal numero', 'Reconoce a la clienta por el número'),
          t('Dice di essere un’AI', 'Dice que es una IA'),
          t('Ordine tecnico: colore, taglio, piega', 'Orden técnico: color, corte, peinado'),
          t('Un solo slot, prezzo e durata del totale', 'Un solo hueco, precio y duración del total')]),
        ('c', t('Cliente', 'Clienta'), t('Perfetto, grazie', 'Perfecto, gracias'), None),
        ('a', t('Agente', 'Agente'), t('Fatto, sei prenotata sabato alle 9:30 con Marta. Ti mando la conferma qui su WhatsApp.',
                                       'Hecho, tienes cita el sábado a las 9:30 con Marta. Te mando la confirmación aquí por WhatsApp.'),
         [t('Scrive nell’agenda del gestionale', 'Escribe en la agenda del software de gestión'),
          t('Dice “prenotato” solo dopo la conferma', 'Dice “reservado” solo tras la confirmación')]),
    ]
    rows = ''
    for i, (who, label, text, notes) in enumerate(msgs):
        ns = ''
        if notes:
            ns = '<ul class="notes">' + ''.join(f'<li>{n}</li>' for n in notes) + '</ul>'
        rows += f'<li class="m m-{who}" style="--i:{i}"><p class="bubble"><b class="who">{label}:</b> {text}</p>{ns}</li>'
    cap = t('Conversazione di esempio su WhatsApp. Accanto a ogni risposta, le regole del salone che l’agente applica.',
            'Conversación de ejemplo por WhatsApp. Junto a cada respuesta, las reglas del salón que aplica el agente.')
    return f'''<figure class="trace" id="esempio">
  <div class="trace-top"><span class="dot" aria-hidden="true"></span>{t('Salone, WhatsApp, giovedì 21:14', 'Salón, WhatsApp, jueves 21:14')}</div>
  <ol class="chat">{rows}</ol>
  <figcaption>{cap}</figcaption>
</figure>'''


# ───────── pagine ─────────
# Ogni pagina restituisce un dizionario: title, desc, crumb, body, ld (lista di nodi JSON-LD aggiuntivi), type.

def faq_home():
    return [
        (t('Cos’è Odyra System?', '¿Qué es Odyra System?'),
         t('Odyra System è un’azienda tecnologica di Milano che costruisce agenti AI di settore: assistenti che rispondono al telefono e su WhatsApp e gestiscono appuntamenti seguendo le regole di un settore preciso. Li collega ai software di gestione, che li offrono ai loro clienti con il proprio marchio.',
           'Odyra System es una empresa tecnológica de Milán que construye agentes IA sectoriales: asistentes que contestan al teléfono y por WhatsApp y gestionan citas siguiendo las reglas de un sector concreto. Los conecta a los software de gestión, que los ofrecen a sus clientes con su propia marca.')),
        (t('Che differenza c’è tra un agente di settore e un’AI generica?', '¿Qué diferencia hay entre un agente sectorial y una IA genérica?'),
         t('Un agente di settore ha le regole di quel mestiere scritte nel codice, non solo in un prompt: per un salone, per esempio, l’ordine colore-taglio-piega, i pacchetti e la regola delle 24 ore per le disdette. Inoltre legge e scrive direttamente nel software di gestione, quindi prenota solo orari realmente liberi.',
           'Un agente sectorial tiene las reglas de ese oficio escritas en el código, no solo en un prompt: en un salón, por ejemplo, el orden color-corte-peinado, los paquetes y la regla de 24 horas para cancelar. Además lee y escribe directamente en el software de gestión, así que solo reserva horarios realmente libres.')),
        (t('Su quali canali lavora l’agente?', '¿En qué canales trabaja el agente?'),
         t('Al telefono, con la voce in tempo reale, e su WhatsApp Business. È lo stesso agente su entrambi i canali, 24 ore su 24.',
           'Por teléfono, con voz en tiempo real, y por WhatsApp Business. Es el mismo agente en los dos canales, las 24 horas.')),
        (t('Dove è già in uso?', '¿Dónde se usa ya?'),
         t('Nel settore beauty: GoAgent è il servizio AI di BOSS per i saloni che usano il gestionale GoWeb, una rete di oltre 1.500 saloni in Italia. È in produzione da giugno 2026.',
           'En el sector beauty: GoAgent es el servicio IA de BOSS para los salones que usan el software GoWeb, una red de más de 1.500 salones en Italia. Está en producción desde junio de 2026.')),
    ]


def page_home():
    body = f'''
<section class="hero"><div class="wrap hero-grid">
  <div class="hero-copy">
    <h1>{t('Agenti AI di settore, dentro i software di gestione.', 'Agentes IA sectoriales, dentro de los software de gestión.')}</h1>
    <p class="lead">{t('Odyra System costruisce agenti AI che rispondono al telefono e su WhatsApp, prenotano e gestiscono appuntamenti seguendo le regole di un settore preciso. Li colleghiamo ai software di gestione, che li offrono ai loro clienti con il proprio marchio.',
                       'Odyra System construye agentes IA que contestan al teléfono y por WhatsApp, reservan y gestionan citas siguiendo las reglas de un sector concreto. Los conectamos a los software de gestión, que los ofrecen a sus clientes con su propia marca.')}</p>
    <p class="btns">{btn(url('partner'), t('Diventa partner', 'Hazte socio'))}{btn('#esempio', t('Guarda un esempio', 'Mira un ejemplo'), 'o')}</p>
  </div>
  {transcript()}
</div></section>

{section(t('Odyra in breve.', 'Odyra en breve.'), facts([
    (t('Cosa fa', 'Qué hace'), t('Agenti AI verticali per settore: rispondono, prenotano, spostano e disdicono appuntamenti, e passano la conversazione a una persona quando serve.', 'Agentes IA verticales por sector: contestan, reservan, cambian y cancelan citas, y pasan la conversación a una persona cuando hace falta.')),
    (t('Per chi', 'Para quién'), t('Software house che sviluppano software di gestione, e aziende con grandi volumi di contatti.', 'Empresas que desarrollan software de gestión, y compañías con grandes volúmenes de contactos.')),
    (t('Canali', 'Canales'), t('Telefono con voce in tempo reale e WhatsApp Business ufficiale.', 'Teléfono con voz en tiempo real y WhatsApp Business oficial.')),
    (t('Modello', 'Modelo'), t('White-label: il software di gestione offre l’agente col proprio marchio e incassa un canone ricorrente; Odyra gestisce tecnologia e operatività.', 'White-label: el software de gestión ofrece el agente con su marca y cobra una cuota recurrente; Odyra gestiona tecnología y operación.')),
    (t('In produzione', 'En producción'), t('Beauty, con GoAgent di BOSS per gli oltre 1.500 saloni GoWeb, da giugno 2026.', 'Beauty, con GoAgent de BOSS para los más de 1.500 salones GoWeb, desde junio de 2026.')),
    (t('Sede', 'Sede'), t('Milano, Italia. Società: Verypos S.r.l.', 'Milán, Italia. Sociedad: Verypos S.r.l.')),
]))}

{section(t('Il modello, in quattro passaggi.', 'El modelo, en cuatro pasos.'), steps([
    (t('Scegliamo un settore', 'Elegimos un sector'), t('E lo studiamo a fondo: come lavora, cosa chiedono i clienti, quali regole contano.', 'Y lo estudiamos a fondo: cómo trabaja, qué piden los clientes, qué reglas cuentan.')),
    (t('Costruiamo l’agente', 'Construimos el agente'), t('Le regole del settore entrano nel codice, non solo in un prompt.', 'Las reglas del sector entran en el código, no solo en un prompt.')),
    (t('Ci colleghiamo al gestionale', 'Nos conectamos al software'), t('Alle API dei software di gestione che quel settore usa già.', 'A las API de los software de gestión que ese sector ya usa.')),
    (t('Il software lo offre ai clienti', 'El software lo ofrece a sus clientes'), t('Con il suo marchio e un canone ricorrente. Odyra gestisce tutto il resto.', 'Con su marca y una cuota recurrente. Odyra gestiona todo lo demás.')),
]), cls='sec-alt')}

{section(t('Perché non basta un’AI generica.', 'Por qué no basta una IA genérica.'), points([
    (t('Conosce il mestiere', 'Conoce el oficio'), t('Le regole di chi fa quel lavoro sono scritte nel codice: l’agente non le dimentica e non le sbaglia.', 'Las reglas de quien hace ese trabajo están escritas en el código: el agente no las olvida ni las confunde.')),
    (t('Lavora dove si lavora già', 'Trabaja donde ya se trabaja'), t('Legge e scrive nel software di gestione. Nessun nuovo strumento da imparare.', 'Lee y escribe en el software de gestión. Ninguna herramienta nueva que aprender.')),
    (t('È gestito da noi', 'Lo gestionamos nosotros'), t('Qualità delle risposte, errori, consumi e passaggio a una persona li seguiamo noi, cliente per cliente.', 'Calidad de las respuestas, errores, consumos y paso a una persona los seguimos nosotros, cliente por cliente.')),
]))}

{section(t('Costruito con la piattaforma Odyra.', 'Construido con la plataforma Odyra.'), f"""<ul class="works">
  <li><h3><a href="{url('goagent')}">GoAgent</a></h3><p>{t('Il servizio AI di BOSS per i saloni che usano GoWeb: risponde, prenota e conferma su WhatsApp. È il nostro riferimento nel beauty.', 'El servicio IA de BOSS para los salones que usan GoWeb: contesta, reserva y confirma por WhatsApp. Es nuestra referencia en beauty.')}</p></li>
  <li><h3><a href="{LINK_HAKO}" rel="noopener">HAKO</a></h3><p>{t('Software proprietario di Odyra per le portinerie dei condomini, venduto direttamente. Ha un sito suo: hakocondomini.com.', 'Software propio de Odyra para las conserjerías de comunidades de vecinos, vendido directamente. Tiene su propia web: hakocondomini.com.')}</p></li>
  <li><h3><a href="{url('misura')}">{t('Progetti su misura', 'Proyectos a medida')}</a></h3><p>{t('Agenti commerciali e di customer service per aziende con grandi volumi, come Gruppo Colzani.', 'Agentes comerciales y de atención al cliente para empresas con grandes volúmenes, como Gruppo Colzani.')}</p></li>
</ul>""", cls='sec-alt')}

{section(t('WhatsApp Business, sui canali ufficiali.', 'WhatsApp Business, por los canales oficiales.'), f'<p class="prose">{t("Odyra è Tech Provider Meta tramite Vonage: attiviamo i numeri WhatsApp Business, gestiamo template e conversazioni. La titolarità dell’account resta sempre al cliente.", "Odyra es Tech Provider de Meta a través de Vonage: activamos los números de WhatsApp Business y gestionamos plantillas y conversaciones. La titularidad de la cuenta sigue siendo siempre del cliente.")}</p>')}

{section(t('Domande frequenti.', 'Preguntas frecuentes.'), faq_list(faq_home()) + f'<p class="more"><a href="{url("faq")}">{t("Tutte le domande", "Todas las preguntas")}</a></p>', cls='sec-alt')}

{cta()}'''
    return dict(
        title=t('Odyra System: agenti AI di settore per i software di gestione', 'Odyra System: agentes IA sectoriales para software de gestión'),
        desc=t('Odyra System costruisce agenti AI di settore che rispondono al telefono e su WhatsApp e prenotano nel gestionale. White-label per i software di gestione. Milano.',
               'Odyra System construye agentes IA sectoriales que contestan al teléfono y por WhatsApp y reservan en el software de gestión. White-label para software de gestión. Milán.'),
        crumb='Home', body=body, type='WebPage',
        ld=[{'@type': 'Service', '@id': f'{SITE}{url("home")}#servizio', 'name': t('Agenti AI di settore in white-label', 'Agentes IA sectoriales en white-label'),
             'serviceType': t('Agente AI vocale e WhatsApp per la gestione degli appuntamenti', 'Agente IA de voz y WhatsApp para la gestión de citas'),
             'provider': {'@id': f'{SITE}/#org'}, 'areaServed': ['IT', 'ES'],
             'audience': {'@type': 'BusinessAudience', 'audienceType': t('Software house di software di gestione', 'Empresas de software de gestión')},
             'description': t('Agenti AI verticali, con le regole del settore nel codice, collegati ai software di gestione e offerti ai loro clienti con il marchio del software.',
                              'Agentes IA verticales, con las reglas del sector en el código, conectados a los software de gestión y ofrecidos a sus clientes con la marca del software.')}],
        faq=faq_home(),
    )


def page_piattaforma():
    body = head_block(
        t('Una piattaforma, cinque strati.', 'Una plataforma, cinco capas.'),
        t('Oltre 18 mesi di sviluppo di un’infrastruttura proprietaria. È la base che ci permette di aprire un nuovo settore o collegare un nuovo software di gestione senza ripartire da zero.',
          'Más de 18 meses de desarrollo de una infraestructura propia. Es la base que nos permite abrir un sector nuevo o conectar un nuevo software de gestión sin empezar de cero.'),
        btn(url('contatti') + '?interesse=partner', t('Richiedi una demo', 'Solicita una demo')))
    layers = [
        (t('Regole di settore', 'Reglas de sector'), t('Il cuore: come lavora quel settore, scritto nel codice. Ordine dei servizi, pacchetti, politiche di disdetta, scelta dell’operatore, passaggio a una persona. Cambia da settore a settore; il resto della piattaforma no.',
                                                         'El núcleo: cómo trabaja ese sector, escrito en el código. Orden de los servicios, paquetes, políticas de cancelación, elección del profesional, paso a una persona. Cambia de un sector a otro; el resto de la plataforma no.')),
        (t('Connettori', 'Conectores'), t('Un connettore dedicato per ogni software di gestione: legge clienti, servizi, operatori e disponibilità, scrive e cancella appuntamenti. Per un nuovo software si scrive il connettore; conversazione e regole restano le stesse.',
                                          'Un conector dedicado para cada software de gestión: lee clientes, servicios, profesionales y disponibilidad, escribe y cancela citas. Para un software nuevo se escribe el conector; conversación y reglas siguen iguales.')),
        (t('Canali', 'Canales'), t('Voce in tempo reale e WhatsApp, con lo stesso agente. WhatsApp Business gestito da Odyra: numeri, template e conversazioni, con la titolarità dell’account al cliente.',
                                   'Voz en tiempo real y WhatsApp, con el mismo agente. WhatsApp Business gestionado por Odyra: números, plantillas y conversaciones, con la titularidad de la cuenta para el cliente.')),
        (t('Gestione operativa', 'Gestión operativa'), t('Un agente per ogni cliente, con dati e configurazione isolati. Limiti e avvisi di consumo, controllo di qualità automatico, monitoraggio degli errori con diagnosi, riassunti per il titolare, passaggio a una persona.',
                                                         'Un agente por cliente, con datos y configuración aislados. Límites y avisos de consumo, control de calidad automático, seguimiento de errores con diagnóstico, resúmenes para el titular, paso a una persona.')),
        (t('Conformità', 'Cumplimiento'), t('L’agente dice sempre di essere un’AI, i dati sono separati per ogni azienda, il trattamento è conforme al GDPR e progettato nel perimetro dell’AI Act. Supportiamo i partner nella documentazione per i settori regolati.',
                                            'El agente dice siempre que es una IA, los datos están separados por empresa, el tratamiento cumple el RGPD y está diseñado dentro del perímetro del AI Act. Ayudamos a los socios con la documentación en sectores regulados.')),
    ]
    body += section(t('Gli strati, dal settore al cliente.', 'Las capas, del sector al cliente.'), steps(layers), cls='layers')
    body += section(t('Come si attiva un nuovo cliente.', 'Cómo se activa un cliente nuevo.'), steps([
        (t('Si crea l’azienda', 'Se crea la empresa'), t('Un solo passaggio crea il cliente con i suoi limiti e le sue impostazioni, senza duplicati.', 'Un solo paso crea el cliente con sus límites y su configuración, sin duplicados.')),
        (t('Staff e listino arrivano da soli', 'Equipo y tarifas llegan solos'), t('Si sincronizzano dal software di gestione ogni notte, e la base di conoscenza dell’agente si aggiorna con loro.', 'Se sincronizan desde el software de gestión cada noche, y la base de conocimiento del agente se actualiza con ellos.')),
        (t('Uno specialista attiva i canali', 'Un especialista activa los canales'), t('Numero, WhatsApp e voce: una procedura di circa dieci minuti.', 'Número, WhatsApp y voz: un procedimiento de unos diez minutos.')),
    ]), intro=t('Dal momento in cui il software di gestione è collegato.', 'Desde que el software de gestión está conectado.'), cls='sec-alt')
    body += section(t('WhatsApp Business ufficiale.', 'WhatsApp Business oficial.'),
                    f'<p class="prose">{t("Odyra è Tech Provider Meta tramite Vonage. Gestiamo l’infrastruttura di numeri e template per tutti i clienti, su più account WhatsApp Business, e i messaggi di conferma e disdetta usano template approvati.", "Odyra es Tech Provider de Meta a través de Vonage. Gestionamos la infraestructura de números y plantillas para todos los clientes, en varias cuentas de WhatsApp Business, y los mensajes de confirmación y cancelación usan plantillas aprobadas.")}</p><p class="small">{t("WhatsApp e Meta sono marchi di Meta Platforms, Inc.; Vonage è un marchio di Vonage Holdings Corp. Odyra non è affiliata a queste società.", "WhatsApp y Meta son marcas de Meta Platforms, Inc.; Vonage es una marca de Vonage Holdings Corp. Odyra no está afiliada a estas empresas.")}</p>')
    body += cta(t('Domande tecniche o di conformità?', '¿Preguntas técnicas o de cumplimiento?'), t('Rispondiamo ai tuoi referenti IT e legali.', 'Respondemos a tus responsables de IT y legales.'), interest='partner')
    return dict(
        title=t('Piattaforma: regole di settore, connettori, voce e WhatsApp | Odyra System', 'Plataforma: reglas de sector, conectores, voz y WhatsApp | Odyra System'),
        desc=t('Come funziona la piattaforma Odyra: regole di settore nel codice, connettori ai software di gestione, voce e WhatsApp, gestione operativa, GDPR e AI Act.',
               'Cómo funciona la plataforma Odyra: reglas de sector en el código, conectores a los software de gestión, voz y WhatsApp, gestión operativa, RGPD y AI Act.'),
        crumb=t('Piattaforma', 'Plataforma'), body=body, type='WebPage', ld=[])


def page_settori():
    body = head_block(
        t('Settori di competenza.', 'Sectores de competencia.'),
        t('Prima di costruire un agente impariamo un settore a fondo: ogni regola, ogni abitudine, ogni caso limite. La piattaforma è la stessa; le regole cambiano da settore a settore.',
          'Antes de construir un agente aprendemos un sector a fondo: cada regla, cada costumbre, cada caso límite. La plataforma es la misma; las reglas cambian de un sector a otro.'))
    body += section(t('Come entriamo in un settore.', 'Cómo entramos en un sector.'), steps([
        (t('Ascoltiamo', 'Escuchamos'), t('Come lavora chi fa quel mestiere, cosa chiedono i clienti, dove si perdono chiamate e tempo.', 'Cómo trabaja quien hace ese oficio, qué piden los clientes, dónde se pierden llamadas y tiempo.')),
        (t('Scriviamo le regole nel codice', 'Escribimos las reglas en el código'), t('Ogni regola del settore diventa codice, così l’agente la rispetta sempre.', 'Cada regla del sector se convierte en código, así el agente la respeta siempre.')),
        (t('Ci colleghiamo', 'Nos conectamos'), t('Ai software di gestione che quel settore usa già.', 'A los software de gestión que ese sector ya usa.')),
        (t('Gestiamo e misuriamo', 'Gestionamos y medimos'), t('Qualità, consumi e risultati, per migliorare ogni settimana.', 'Calidad, consumos y resultados, para mejorar cada semana.')),
    ]))
    body += section(t('Beauty: parrucchieri e centri estetici.', 'Beauty: peluquerías y centros de estética.'),
                    f'''<p class="prose">{t('È il settore in cui siamo partiti. Con BOSS e il suo gestionale GoWeb l’agente è disponibile per una rete di oltre 1.500 saloni, con il nome GoAgent. Ecco alcune delle regole che segue:', 'Es el sector en el que empezamos. Con BOSS y su software GoWeb, el agente está disponible para una red de más de 1.500 salones, con el nombre GoAgent. Estas son algunas de las reglas que sigue:')}</p>
{salon_rules(8)}
<p class="more"><a href="{url('goagent')}">{t('Tutte le regole e la storia di GoAgent', 'Todas las reglas y la historia de GoAgent')}</a></p>''', cls='sec-alt')
    others = [
        (t('Dentale', 'Dental'), t('Studi dentistici e cliniche odontoiatriche.', 'Clínicas dentales.')),
        (t('Autofficine', 'Talleres'), t('Officine meccaniche e centri di assistenza auto.', 'Talleres mecánicos y centros de servicio del automóvil.')),
        (t('Ospitalità', 'Hostelería'), t('Hotel, strutture ricettive e ristorazione.', 'Hoteles, alojamientos y restauración.')),
        (t('Veterinari', 'Veterinarios'), t('Ambulatori e cliniche veterinarie.', 'Consultas y clínicas veterinarias.')),
    ]
    body += section(t('Gli altri settori di competenza.', 'Los demás sectores de competencia.'), points(others, 'points cols4'),
                    intro=t('Stessa piattaforma, regole diverse. Se il tuo software di gestione lavora in uno di questi settori, o in un altro, parliamone.',
                            'Misma plataforma, reglas distintas. Si tu software de gestión trabaja en uno de estos sectores, o en otro, hablemos.'))
    body += cta(t('Hai un software di gestione?', '¿Tienes un software de gestión?'), t('Raccontaci il tuo settore: vediamo insieme come portare l’agente ai tuoi clienti.', 'Cuéntanos tu sector: vemos juntos cómo llevar el agente a tus clientes.'), interest='partner')
    return dict(
        title=t('Settori: beauty, dentale, autofficine, ospitalità, veterinari | Odyra System', 'Sectores: beauty, dental, talleres, hostelería, veterinarios | Odyra System'),
        desc=t('Odyra costruisce agenti AI con le regole di ogni settore nel codice. Beauty in produzione con GoAgent; competenze in dentale, autofficine, ospitalità e veterinari.',
               'Odyra construye agentes IA con las reglas de cada sector en el código. Beauty en producción con GoAgent; competencias en dental, talleres, hostelería y veterinarios.'),
        crumb=t('Settori', 'Sectores'), body=body, type='WebPage', ld=[])


def faq_partner():
    return [
        (t('Cosa deve fare un software di gestione per diventare partner?', '¿Qué tiene que hacer un software de gestión para ser socio?'),
         t('Dare accesso alle API essenziali: ricerca del cliente, disponibilità, creazione e cancellazione degli appuntamenti. Il connettore lo scrive Odyra, senza toccare il cuore del software.',
           'Dar acceso a las API esenciales: búsqueda de cliente, disponibilidad, creación y cancelación de citas. El conector lo escribe Odyra, sin tocar el núcleo del software.')),
        (t('Come guadagna il partner?', '¿Cómo gana el socio?'),
         t('Con un canone ricorrente da ogni cliente che attiva l’agente, con revenue condivisa con Odyra. La formula si definisce insieme.',
           'Con una cuota recurrente de cada cliente que activa el agente, con ingresos compartidos con Odyra. La fórmula se define juntos.')),
        (t('Con quale marchio arriva ai clienti?', '¿Con qué marca llega a los clientes?'),
         t('Con quello del partner: interfacce, messaggi e dashboard portano il suo nome e il suo logo.', 'Con la del socio: interfaces, mensajes y paneles llevan su nombre y su logo.')),
        (t('Chi segue i clienti dopo l’attivazione?', '¿Quién atiende a los clientes después de la activación?'),
         t('Odyra: onboarding, controllo di qualità, errori, consumi, WhatsApp Business e assistenza tecnica.', 'Odyra: alta, control de calidad, errores, consumos, WhatsApp Business y soporte técnico.')),
    ]


def page_partner():
    vtag, vld = video('partner-program', t('Il programma partner di Odyra', 'El programa de socios de Odyra'),
                      t('Il programma partner spiegato in pochi minuti.', 'El programa de socios explicado en pocos minutos.'))
    body = head_block(
        t('Un’AI di settore per i tuoi clienti, col tuo marchio.', 'Una IA sectorial para tus clientes, con tu marca.'),
        t('Il tuo software di gestione offre un agente che risponde, prenota e organizza al posto del cliente. Tu porti i clienti; Odyra porta prodotto, tecnologia e gestione.',
          'Tu software de gestión ofrece un agente que contesta, reserva y organiza en lugar del cliente. Tú aportas los clientes; Odyra aporta producto, tecnología y gestión.'),
        btn(url('contatti') + '?interesse=partner', t('Diventa partner', 'Hazte socio')))
    body += section(t('Cosa fai tu, cosa facciamo noi.', 'Qué haces tú, qué hacemos nosotros.'), facts([
        (t('Il partner', 'El socio'), t('Offre il servizio ai suoi clienti col suo marchio e dà accesso alle API: ricerca cliente, disponibilità, creazione e cancellazione appuntamenti.', 'Ofrece el servicio a sus clientes con su marca y da acceso a las API: búsqueda de cliente, disponibilidad, creación y cancelación de citas.')),
        ('Odyra', t('Agente di settore, connettore al software, onboarding dei clienti, dashboard per i titolari, WhatsApp Business, controlli di qualità e assistenza.', 'Agente sectorial, conector al software, alta de clientes, paneles para los titulares, WhatsApp Business, controles de calidad y soporte.')),
        (t('Il marchio', 'La marca'), t('Interfacce, messaggi e dashboard portano il logo del partner.', 'Interfaces, mensajes y paneles llevan el logo del socio.')),
        (t('Il ricavo', 'Los ingresos'), t('Un nuovo canone ricorrente da ogni cliente che attiva l’agente, con revenue condivisa con Odyra.', 'Una nueva cuota recurrente de cada cliente que activa el agente, con ingresos compartidos con Odyra.')),
    ]))
    body += section(t('Come si parte.', 'Cómo se empieza.'), steps([
        (t('Collegamento', 'Conexión'), t('Un connettore dedicato collega il tuo software alla piattaforma, senza toccarne il cuore.', 'Un conector dedicado une tu software a la plataforma, sin tocar su núcleo.')),
        (t('Attivazione dei clienti', 'Activación de clientes'), t('Staff e listino si sincronizzano da soli. Numero, WhatsApp e voce li configura uno specialista Odyra in circa dieci minuti.', 'Equipo y tarifas se sincronizan solos. Número, WhatsApp y voz los configura un especialista de Odyra en unos diez minutos.')),
        (t('Gestione continua', 'Gestión continua'), t('Controlliamo qualità, errori e consumi. Il cliente vede tutto nella sua dashboard.', 'Controlamos calidad, errores y consumos. El cliente lo ve todo en su panel.')),
    ]) + vtag, cls='sec-alt')
    body += section(t('Un caso reale: BOSS e GoWeb.', 'Un caso real: BOSS y GoWeb.'),
                    f'<p class="prose">{t("BOSS sviluppa GoWeb, tra i software più diffusi per parrucchieri e centri estetici in Italia, con oltre 1.500 saloni. Con Odyra ha lanciato GoAgent con il proprio marchio.", "BOSS desarrolla GoWeb, uno de los software más difundidos para peluquerías y centros de estética en Italia, con más de 1.500 salones. Con Odyra ha lanzado GoAgent con su propia marca.")}</p><p class="more"><a href="{url("goagent")}">{t("La storia di GoAgent", "La historia de GoAgent")}</a></p>')
    body += section(t('Domande dei partner.', 'Preguntas de los socios.'), faq_list(faq_partner()), cls='sec-alt')
    body += cta(t('Porta l’AI nel tuo software di gestione.', 'Lleva la IA a tu software de gestión.'), t('Parliamo di integrazione, formula e tempi.', 'Hablemos de integración, fórmula y plazos.'), t('Diventa partner', 'Hazte socio'), 'partner')
    ld = [{'@type': 'Service', 'name': t('Programma partner Odyra per software di gestione', 'Programa de socios Odyra para software de gestión'),
           'serviceType': t('Agente AI in white-label', 'Agente IA en white-label'), 'provider': {'@id': f'{SITE}/#org'},
           'audience': {'@type': 'BusinessAudience', 'audienceType': t('Software house di software di gestione', 'Empresas de software de gestión')},
           'description': t('Il software di gestione offre ai suoi clienti un agente AI di settore col proprio marchio, con canone ricorrente e revenue condivisa; Odyra fornisce prodotto, connettore, onboarding e gestione.',
                            'El software de gestión ofrece a sus clientes un agente IA sectorial con su marca, con cuota recurrente e ingresos compartidos; Odyra aporta producto, conector, alta y gestión.')}]
    if vld:
        ld.append(vld)
    return dict(
        title=t('Programma partner per software di gestione: AI in white-label | Odyra System', 'Programa de socios para software de gestión: IA en white-label | Odyra System'),
        desc=t('Offri ai clienti del tuo software di gestione un agente AI di settore col tuo marchio. Canone ricorrente, revenue condivisa, tecnologia e gestione a carico di Odyra.',
               'Ofrece a los clientes de tu software de gestión un agente IA sectorial con tu marca. Cuota recurrente, ingresos compartidos, tecnología y gestión a cargo de Odyra.'),
        crumb=t('Per i software di gestione', 'Para software de gestión'), body=body, type='WebPage', ld=ld, faq=faq_partner())


def page_goagent():
    vtag, vld = video('goagent', 'GoAgent', t('Il video di presentazione di GoAgent.', 'El vídeo de presentación de GoAgent.'))
    shots = [
        ('panoramica', t('Panoramica: chiamate, appuntamenti fissati dall’AI, conversione e ore risparmiate.', 'Resumen: llamadas, citas fijadas por la IA, conversión y horas ahorradas.')),
        ('inbox-whatsapp', t('Inbox WhatsApp: il titolare prende in carico la conversazione e la restituisce all’AI.', 'Bandeja de WhatsApp: el titular toma la conversación y se la devuelve a la IA.')),
        ('chiamate', t('Chiamate: trascrizione, riassunto e dettagli dell’appuntamento.', 'Llamadas: transcripción, resumen y detalles de la cita.')),
        ('pacchetti', t('Pacchetti: servizi abbinati con prezzo e durata totali.', 'Paquetes: servicios combinados con precio y duración totales.')),
        ('consumi', t('Consumi del piano e impostazioni dell’agente.', 'Consumo del plan y ajustes del agente.')),
    ]
    gallery = '<div class="shots">' + ''.join(
        f'<figure><img src="/assets/img/goagent-{n}.webp" width="1200" height="750" loading="lazy" decoding="async" alt="{e(c)}"><figcaption>{c}</figcaption></figure>' for n, c in shots) + '</div>'
    body = head_block(
        t('GoAgent: l’agente AI dei saloni GoWeb.', 'GoAgent: el agente IA de los salones GoWeb.'),
        t('GoAgent è il servizio AI di BOSS per parrucchieri e centri estetici che usano GoWeb. Risponde al telefono e su WhatsApp, giorno e notte, e prenota direttamente nell’agenda del salone. Lo ha costruito e lo gestisce Odyra System.',
          'GoAgent es el servicio IA de BOSS para peluquerías y centros de estética que usan GoWeb. Contesta al teléfono y por WhatsApp, día y noche, y reserva directamente en la agenda del salón. Lo ha construido y lo gestiona Odyra System.'),
        btn(LINK_BOSS, t('Scopri GoAgent su BOSS', 'Descubre GoAgent en BOSS'), 'p', ' rel="noopener"'))
    body += section(t('La storia.', 'La historia.'), steps([
        (t('Il problema', 'El problema'), t('I saloni perdono prenotazioni ogni giorno: il telefono squilla mentre lo staff lavora, i messaggi arrivano a negozio chiuso.', 'Los salones pierden reservas cada día: el teléfono suena mientras el equipo trabaja, los mensajes llegan con el local cerrado.')),
        (t('La scelta di BOSS', 'La decisión de BOSS'), t('BOSS sviluppa GoWeb, usato da oltre 1.500 saloni. Voleva offrire ai clienti un assistente AI vero, integrato nel gestionale, senza costruirlo in casa.', 'BOSS desarrolla GoWeb, usado por más de 1.500 salones. Quería ofrecer a sus clientes un asistente IA de verdad, integrado en el software, sin construirlo en casa.')),
        (t('Il lancio', 'El lanzamiento'), t('Odyra ha costruito l’agente, l’onboarding dei saloni, la dashboard e la gestione. GoAgent è in produzione da giugno 2026 ed è stato presentato alla convention BOSS di ottobre 2026, davanti a oltre 300 persone.', 'Odyra construyó el agente, el alta de los salones, el panel y la gestión. GoAgent está en producción desde junio de 2026 y se presentó en la convención de BOSS de octubre de 2026, ante más de 300 personas.')),
    ]) + vtag)
    body += section(t('Conosce il mestiere.', 'Conoce el oficio.'), salon_rules(),
                    intro=t('Le regole del salone sono nel codice, non solo in un prompt. Queste sono le principali.', 'Las reglas del salón están en el código, no solo en un prompt. Estas son las principales.'), cls='sec-alt')
    body += section(t('Voce e WhatsApp.', 'Voz y WhatsApp.'), points([
        (t('Un solo agente', 'Un solo agente'), t('Risponde al telefono e su WhatsApp, 24 ore su 24, anche su più conversazioni insieme.', 'Contesta al teléfono y por WhatsApp, las 24 horas, incluso en varias conversaciones a la vez.')),
        (t('Dentro GoWeb', 'Dentro de GoWeb'), t('Legge servizi, operatori, turni e disponibilità e scrive gli appuntamenti nell’agenda.', 'Lee servicios, profesionales, turnos y disponibilidad y escribe las citas en la agenda.')),
        (t('Parla come un salone', 'Habla como un salón'), t('Frasi brevi, una domanda alla volta, il nome della cliente e la sua ultima visita.', 'Frases cortas, una pregunta cada vez, el nombre de la clienta y su última visita.')),
        (t('Conferme su WhatsApp', 'Confirmaciones por WhatsApp'), t('Conferma e disdetta di ogni appuntamento, con messaggi approvati.', 'Confirmación y cancelación de cada cita, con mensajes aprobados.')),
    ], 'points cols4'))
    body += section(t('La dashboard del titolare.', 'El panel del titular.'), gallery,
                    intro=t('Schermate reali della dashboard, con dati di prova.', 'Pantallas reales del panel, con datos de prueba.'), cls='sec-alt')
    body += section(t('In arrivo.', 'Próximamente.'), f'<p class="prose">{t("Chiamate in uscita ai clienti che non tornano in salone: l’agente li richiama, al telefono o su WhatsApp, e li riporta in agenda.", "Llamadas salientes a los clientes que no vuelven al salón: el agente los llama, por teléfono o por WhatsApp, y los vuelve a poner en la agenda.")}</p>')
    body += cta(t('Hai un software di gestione come GoWeb?', '¿Tienes un software de gestión como GoWeb?'), t('Possiamo fare lo stesso per i tuoi clienti, col tuo marchio.', 'Podemos hacer lo mismo para tus clientes, con tu marca.'), t('Diventa partner', 'Hazte socio'), 'partner')
    ld = [{'@type': 'SoftwareApplication', '@id': f'{SITE}{url("goagent")}#app', 'name': 'GoAgent',
           'applicationCategory': 'BusinessApplication', 'operatingSystem': 'Web',
           'description': t('Agente AI per saloni di parrucchieri e centri estetici: risponde al telefono e su WhatsApp e prenota nell’agenda del gestionale GoWeb.',
                            'Agente IA para peluquerías y centros de estética: contesta al teléfono y por WhatsApp y reserva en la agenda del software GoWeb.'),
           'brand': {'@type': 'Brand', 'name': 'BOSS'}, 'creator': {'@id': f'{SITE}/#org'},
           'audience': {'@type': 'BusinessAudience', 'audienceType': t('Parrucchieri e centri estetici', 'Peluquerías y centros de estética')},
           'screenshot': [f'{SITE}/assets/img/goagent-{n}.webp' for n, _ in shots]}]
    if vld:
        ld.append(vld)
    return dict(
        title=t('GoAgent: agente AI per parrucchieri e centri estetici GoWeb | Odyra System', 'GoAgent: agente IA para peluquerías y centros de estética GoWeb | Odyra System'),
        desc=t('GoAgent risponde al telefono e su WhatsApp per i saloni GoWeb e prenota nell’agenda. Servizio di BOSS costruito e gestito da Odyra System. In produzione da giugno 2026.',
               'GoAgent contesta al teléfono y por WhatsApp para los salones GoWeb y reserva en la agenda. Servicio de BOSS construido y gestionado por Odyra System. En producción desde junio de 2026.'),
        crumb='GoAgent', body=body, type='WebPage', ld=ld)


def page_misura():
    body = head_block(
        t('Progetti su misura per aziende con grandi volumi.', 'Proyectos a medida para empresas con grandes volúmenes.'),
        t('La stessa piattaforma, applicata ai processi di una singola azienda: vendite, customer service e back office, integrati con CRM ed ERP.',
          'La misma plataforma, aplicada a los procesos de una sola empresa: ventas, atención al cliente y back office, integrados con CRM y ERP.'),
        btn(url('contatti') + '?interesse=misura', t('Parliamo del progetto', 'Hablemos del proyecto')))
    body += section(t('Dove l’AI fa lavoro vero.', 'Donde la IA hace trabajo de verdad.'), points([
        (t('Vendite', 'Ventas'), t('Un agente richiama ogni lead in pochi secondi, lo qualifica con domande strutturate e fissa l’appuntamento nel calendario del team. Chi non risponde al telefono viene ricontattato su WhatsApp.', 'Un agente llama a cada lead en pocos segundos, lo cualifica con preguntas estructuradas y fija la cita en el calendario del equipo. A quien no contesta al teléfono se le escribe por WhatsApp.')),
        (t('Customer service', 'Atención al cliente'), t('Voce, WhatsApp ed e-mail, con risposte coerenti e passaggio a una persona quando serve.', 'Voz, WhatsApp y correo, con respuestas coherentes y paso a una persona cuando hace falta.')),
        (t('Back office', 'Back office'), t('Automazioni sui processi ripetitivi, tra i sistemi che l’azienda usa già.', 'Automatizaciones de procesos repetitivos, entre los sistemas que la empresa ya usa.')),
    ]))
    body += section(t('Il caso Gruppo Colzani.', 'El caso Gruppo Colzani.'),
                    f'<p class="prose">{t("Gruppo Colzani, dietro Sportit.com e Global Trading, genera centinaia di lead a ogni campagna. L’agente commerciale di Odyra scrive subito su WhatsApp, richiama in pochi secondi, qualifica il contatto, fissa l’appuntamento e registra l’esito nel CRM. La collaborazione prosegue con l’automazione del customer service via e-mail per i marketplace.", "Gruppo Colzani, detrás de Sportit.com y Global Trading, genera cientos de leads en cada campaña. El agente comercial de Odyra escribe enseguida por WhatsApp, llama en pocos segundos, cualifica el contacto, fija la cita y registra el resultado en el CRM. La colaboración sigue con la automatización de la atención al cliente por correo para los marketplaces.")}</p>', cls='sec-alt')
    body += section(t('Come lavoriamo.', 'Cómo trabajamos.'), steps([
        (t('Capiamo il processo', 'Entendemos el proceso'), t('Dove si perdono chiamate, tempo e margine.', 'Dónde se pierden llamadas, tiempo y margen.')),
        (t('Disegniamo e integriamo', 'Diseñamos e integramos'), t('Cosa sa l’agente, quando passa la mano a una persona, con quali sistemi si collega.', 'Qué sabe el agente, cuándo pasa a una persona, con qué sistemas se conecta.')),
        (t('Misuriamo', 'Medimos'), t('Chiamate, esiti e tempi in una dashboard, per migliorare ogni settimana.', 'Llamadas, resultados y tiempos en un panel, para mejorar cada semana.')),
    ]))
    body += cta(t('Hai un processo da automatizzare?', '¿Tienes un proceso que automatizar?'), t('Raccontacelo: ti diciamo cosa si può fare e in quanto tempo.', 'Cuéntanoslo: te decimos qué se puede hacer y en cuánto tiempo.'), interest='misura')
    return dict(
        title=t('Agenti AI su misura per vendite e customer service | Odyra System', 'Agentes IA a medida para ventas y atención al cliente | Odyra System'),
        desc=t('Agenti AI e automazioni su misura per aziende con grandi volumi: richiamo dei lead in pochi secondi, qualifica, appuntamenti, customer service, integrazione con CRM ed ERP.',
               'Agentes IA y automatizaciones a medida para empresas con grandes volúmenes: llamada a leads en segundos, cualificación, citas, atención al cliente, integración con CRM y ERP.'),
        crumb=t('Su misura', 'A medida'), body=body, type='WebPage',
        ld=[{'@type': 'Service', 'name': t('Agenti AI su misura', 'Agentes IA a medida'), 'provider': {'@id': f'{SITE}/#org'},
             'serviceType': t('Automazione di vendite, customer service e back office con agenti AI', 'Automatización de ventas, atención al cliente y back office con agentes IA'),
             'areaServed': ['IT', 'ES']}])


def page_chi():
    body = head_block(
        t('Un settore alla volta.', 'Un sector cada vez.'),
        t('Odyra System è un gruppo tecnologico di Milano. Impariamo un settore a fondo e costruiamo il software con l’AI che fa il lavoro. Lo portiamo ai clienti in tre modi.',
          'Odyra System es un grupo tecnológico de Milán. Aprendemos un sector a fondo y construimos el software con la IA que hace el trabajo. Lo llevamos a los clientes de tres maneras.'))
    body += section(t('Tre modi di portare l’AI al lavoro.', 'Tres maneras de llevar la IA al trabajo.'), points([
        (t('Con i software di gestione', 'Con los software de gestión'), t('Agenti di settore in white-label, dentro il software che i clienti usano già. Nel beauty, con GoAgent di BOSS.', 'Agentes sectoriales en white-label, dentro del software que los clientes ya usan. En beauty, con GoAgent de BOSS.')),
        (t('Con prodotti propri', 'Con productos propios'), t('Software proprietari venduti direttamente, come HAKO per le portinerie dei condomini.', 'Software propio vendido directamente, como HAKO para las conserjerías de comunidades de vecinos.')),
        (t('Su misura', 'A medida'), t('Agenti e automazioni per aziende con grandi volumi.', 'Agentes y automatizaciones para empresas con grandes volúmenes.')),
    ]))
    body += section(t('Missione e visione.', 'Misión y visión.'), facts([
        (t('Missione', 'Misión'), t('Dare a ogni azienda, dal singolo salone al gruppo industriale, una forza lavoro AI affidabile, integrata e misurabile.', 'Dar a cada empresa, del salón individual al grupo industrial, una fuerza de trabajo IA fiable, integrada y medible.')),
        (t('Visione', 'Visión'), t('Diventare il gruppo europeo di riferimento per i software AI verticali: prodotti proprietari, ciascuno leader nel suo mercato, su un’unica infrastruttura condivisa.', 'Ser el grupo europeo de referencia en software IA vertical: productos propios, cada uno líder en su mercado, sobre una única infraestructura compartida.')),
    ]), cls='sec-alt')
    body += section(t('Dati societari.', 'Datos de la empresa.'), facts([
        (t('Società', 'Sociedad'), COMPANY['legal']),
        (t('Sede', 'Sede'), f"{COMPANY['street']}, {COMPANY['zip']} {COMPANY['city']}"),
        (t('Partita IVA', 'NIF-IVA'), COMPANY['vat']),
        ('REA', COMPANY['rea']),
        (t('Contatto', 'Contacto'), f'<a href="mailto:{EMAIL}">{EMAIL}</a>'),
    ]))
    body += cta(t('Lavoriamo insieme.', 'Trabajemos juntos.'), t('Che tu sia un software di gestione o un’azienda, raccontaci il tuo caso.', 'Seas un software de gestión o una empresa, cuéntanos tu caso.'))
    return dict(
        title=t('Chi siamo: Odyra System, gruppo tecnologico di Milano', 'Quiénes somos: Odyra System, grupo tecnológico de Milán'),
        desc=t('Odyra System (Verypos S.r.l.) è un gruppo tecnologico di Milano che costruisce software AI verticali: agenti di settore in white-label, prodotti propri come HAKO e progetti su misura.',
               'Odyra System (Verypos S.r.l.) es un grupo tecnológico de Milán que construye software IA vertical: agentes sectoriales en white-label, productos propios como HAKO y proyectos a medida.'),
        crumb=t('Chi siamo', 'Quiénes somos'), body=body, type='AboutPage', ld=[])


def faq_all():
    return faq_home() + faq_partner() + [
        (t('Con quali software di gestione funziona?', '¿Con qué software de gestión funciona?'),
         t('Con ogni software di gestione che espone le API per clienti, disponibilità e appuntamenti: per ciascuno Odyra scrive un connettore dedicato. Oggi è in produzione con GoWeb di BOSS.',
           'Con cualquier software de gestión que exponga API de clientes, disponibilidad y citas: para cada uno Odyra escribe un conector dedicado. Hoy está en producción con GoWeb de BOSS.')),
        (t('Quanto ci vuole per attivare un nuovo cliente?', '¿Cuánto se tarda en activar un cliente nuevo?'),
         t('Con il software di gestione già collegato, staff e listino si sincronizzano da soli e uno specialista Odyra attiva numero, WhatsApp e voce in circa dieci minuti.',
           'Con el software de gestión ya conectado, equipo y tarifas se sincronizan solos y un especialista de Odyra activa número, WhatsApp y voz en unos diez minutos.')),
        (t('L’agente dice di essere un’intelligenza artificiale?', '¿El agente dice que es una inteligencia artificial?'),
         t('Sì, sempre, sia al telefono sia su WhatsApp, come richiede l’AI Act europeo.', 'Sí, siempre, tanto por teléfono como por WhatsApp, como exige el AI Act europeo.')),
        (t('Cosa succede se l’agente non sa rispondere?', '¿Qué pasa si el agente no sabe responder?'),
         t('Passa la conversazione a una persona, anche durante una chiamata. Su WhatsApp il titolare può prendere in carico la conversazione e restituirla all’AI quando vuole.',
           'Pasa la conversación a una persona, incluso durante una llamada. En WhatsApp el titular puede tomar la conversación y devolvérsela a la IA cuando quiera.')),
        (t('Come vengono trattati i dati?', '¿Cómo se tratan los datos?'),
         t('Ogni azienda ha un agente con dati e configurazione isolati. Il trattamento è conforme al GDPR e progettato nel perimetro dell’AI Act.',
           'Cada empresa tiene un agente con datos y configuración aislados. El tratamiento cumple el RGPD y está diseñado dentro del perímetro del AI Act.')),
        (t('Di chi è il numero WhatsApp Business?', '¿De quién es el número de WhatsApp Business?'),
         t('Del cliente. Odyra, come Tech Provider Meta tramite Vonage, attiva il numero e gestisce template e conversazioni, ma la titolarità dell’account resta al cliente.',
           'Del cliente. Odyra, como Tech Provider de Meta a través de Vonage, activa el número y gestiona plantillas y conversaciones, pero la titularidad de la cuenta sigue siendo del cliente.')),
        (t('Cos’è HAKO?', '¿Qué es HAKO?'),
         t('HAKO è un software proprietario di Odyra per le portinerie dei condomini, venduto direttamente. Ha un sito dedicato: hakocondomini.com.',
           'HAKO es un software propio de Odyra para las conserjerías de comunidades de vecinos, vendido directamente. Tiene una web propia: hakocondomini.com.')),
        (t('Odyra lavora anche con aziende che non sono software house?', '¿Odyra trabaja también con empresas que no son de software?'),
         t('Sì, con progetti su misura per aziende con grandi volumi: agenti commerciali che richiamano i lead in pochi secondi, customer service e automazioni di back office, integrati con CRM ed ERP.',
           'Sí, con proyectos a medida para empresas con grandes volúmenes: agentes comerciales que llaman a los leads en segundos, atención al cliente y automatizaciones de back office, integrados con CRM y ERP.')),
        (t('Chi c’è dietro Odyra System?', '¿Quién está detrás de Odyra System?'),
         t('Odyra System è un marchio di Verypos S.r.l., con sede in Viale Papiniano 8, 20123 Milano. Partita IVA 11630390968.',
           'Odyra System es una marca de Verypos S.r.l., con sede en Viale Papiniano 8, 20123 Milán (Italia). NIF-IVA 11630390968.')),
    ]


def page_faq():
    body = head_block(t('Domande frequenti.', 'Preguntas frecuentes.'),
                      t('Cosa fa Odyra, come funzionano gli agenti di settore, come si diventa partner. Risposte brevi e precise.',
                        'Qué hace Odyra, cómo funcionan los agentes sectoriales, cómo hacerse socio. Respuestas breves y precisas.'))
    body += f'<section class="sec"><div class="wrap">{faq_list(faq_all())}</div></section>'
    body += cta(t('Non trovi la risposta?', '¿No encuentras la respuesta?'), t('Scrivici: rispondiamo entro un giorno lavorativo.', 'Escríbenos: respondemos en un día laborable.'), t('Scrivici', 'Escríbenos'))
    return dict(
        title=t('Domande frequenti su Odyra System e gli agenti AI di settore', 'Preguntas frecuentes sobre Odyra System y los agentes IA sectoriales'),
        desc=t('Risposte su Odyra System: cos’è un agente AI di settore, canali, software di gestione supportati, partnership white-label, GDPR, AI Act e WhatsApp Business.',
               'Respuestas sobre Odyra System: qué es un agente IA sectorial, canales, software de gestión compatibles, alianzas white-label, RGPD, AI Act y WhatsApp Business.'),
        crumb=t('Domande frequenti', 'Preguntas frecuentes'), body=body, type='FAQPage', ld=[], faq=faq_all(), faq_main=True)


def page_contatti():
    opts = [('partner', t('Partnership per software di gestione', 'Alianza para software de gestión')), ('goagent', 'GoAgent'),
            ('hako', 'HAKO'), ('misura', t('Progetto su misura', 'Proyecto a medida')), ('altro', t('Altro', 'Otro'))]
    pv = url('privacy')
    body = head_block(t('Parliamo del tuo caso.', 'Hablemos de tu caso.'),
                      t('Raccontaci come lavori oggi. Rispondiamo entro un giorno lavorativo.', 'Cuéntanos cómo trabajas hoy. Respondemos en un día laborable.'))
    body += f'''<section class="sec"><div class="wrap contact-grid">
  <form class="form" id="form-contatti" data-md="skip" novalidate data-ok="{e(t('Richiesta inviata. Ti rispondiamo entro un giorno lavorativo.', 'Solicitud enviada. Respondemos en un día laborable.'))}" data-err="{e(t('Invio non riuscito. Scrivici a ' + EMAIL + '.', 'No se pudo enviar. Escríbenos a ' + EMAIL + '.'))}" data-mail="{e(t('Si è aperto il tuo programma di posta con la richiesta già scritta: premi Invia.', 'Se ha abierto tu programa de correo con la solicitud ya escrita: pulsa Enviar.'))}">
    <p class="f2"><label>{t('Nome e cognome', 'Nombre y apellidos')}<input name="nome" autocomplete="name" required></label><label>{t('Azienda', 'Empresa')}<input name="azienda" autocomplete="organization"></label></p>
    <p class="f2"><label>E-mail<input name="email" type="email" autocomplete="email" required></label><label>{t('Telefono', 'Teléfono')}<input name="telefono" type="tel" autocomplete="tel"></label></p>
    <p><label>{t('Di cosa hai bisogno?', '¿Qué necesitas?')}<select name="interesse">{''.join(f'<option value="{v}">{l}</option>' for v, l in opts)}</select></label></p>
    <p><label>{t('Messaggio', 'Mensaje')}<textarea name="messaggio" rows="5" required></textarea></label></p>
    <p class="check"><label><input type="checkbox" name="privacy" required> <span>{t(f'Ho letto l’<a href="{pv}">informativa privacy</a> e acconsento a essere ricontattato.', f'He leído la <a href="{pv}">política de privacidad</a> y acepto ser contactado.')}</span></label></p>
    <p><button class="btn btn-p" type="submit">{t('Invia la richiesta', 'Enviar la solicitud')}</button></p>
    <p class="form-msg" id="form-msg" role="status" aria-live="polite"></p>
  </form>
  <aside class="contact-side">
    {facts([('E-mail', f'<a href="mailto:{EMAIL}">{EMAIL}</a>'), (t('Sede', 'Sede'), f"{COMPANY['legal']}<br>{COMPANY['street']}<br>{COMPANY['zip']} {COMPANY['city']} (MI), {t('Italia', 'Italia')}")])}
  </aside>
</div></section>'''
    return dict(
        title=t('Contatti: richiedi una demo | Odyra System', 'Contacto: solicita una demo | Odyra System'),
        desc=t('Contatta Odyra System per una demo degli agenti AI di settore, una partnership per il tuo software di gestione o un progetto su misura. Milano, team@odyrasystemautomation.it.',
               'Contacta con Odyra System para una demo de los agentes IA sectoriales, una alianza para tu software de gestión o un proyecto a medida. Milán, team@odyrasystemautomation.it.'),
        crumb=t('Contatti', 'Contacto'), body=body, type='ContactPage', ld=[])


def page_privacy():
    body = head_block(t('Informativa sulla privacy.', 'Política de privacidad.'), t('Come trattiamo i dati raccolti da questo sito.', 'Cómo tratamos los datos que recoge este sitio.'))
    # Bozza: da far rivedere a un legale prima di considerarla definitiva.
    body += f'''<section class="sec"><div class="wrap prose-block">
<h2>{t('Titolare del trattamento', 'Responsable del tratamiento')}</h2>
<p>{COMPANY['legal']}, {COMPANY['street']}, {COMPANY['zip']} {COMPANY['city']}. {t('Partita IVA', 'NIF-IVA')} {COMPANY['vat']}. <a href="mailto:{EMAIL}">{EMAIL}</a></p>
<h2>{t('Dati raccolti', 'Datos recogidos')}</h2>
<p>{t('Con il modulo contatti raccogliamo nome, azienda, e-mail, telefono e messaggio, al solo scopo di rispondere alla tua richiesta. Li conserviamo per il tempo necessario a gestirla.', 'Con el formulario de contacto recogemos nombre, empresa, correo, teléfono y mensaje, solo para responder a tu solicitud. Los conservamos el tiempo necesario para gestionarla.')}</p>
<h2>{t('Cookie e servizi esterni', 'Cookies y servicios externos')}</h2>
<p>{t('Il sito non usa cookie di profilazione né strumenti di tracciamento. I caratteri sono ospitati sul nostro server: nessun dato viene inviato a servizi di terzi per visualizzare le pagine.', 'El sitio no usa cookies de perfilado ni herramientas de seguimiento. Las fuentes están alojadas en nuestro servidor: no se envía ningún dato a terceros para mostrar las páginas.')}</p>
<h2>{t('I tuoi diritti', 'Tus derechos')}</h2>
<p>{t(f'Puoi chiedere accesso, rettifica, cancellazione e opposizione scrivendo a <a href="mailto:{EMAIL}">{EMAIL}</a>. Puoi anche presentare reclamo al Garante per la protezione dei dati personali.', f'Puedes pedir acceso, rectificación, supresión y oposición escribiendo a <a href="mailto:{EMAIL}">{EMAIL}</a>. También puedes presentar una reclamación ante la autoridad de protección de datos.')}</p>
</div></section>'''
    return dict(title=t('Informativa privacy | Odyra System', 'Política de privacidad | Odyra System'),
                desc=t('Informativa sul trattamento dei dati personali del sito Odyra System.', 'Política de tratamiento de datos personales del sitio Odyra System.'),
                crumb='Privacy', body=body, type='WebPage', ld=[], noindex=True)


def page_404():
    body = head_block(t('Questa pagina non esiste.', 'Esta página no existe.'),
                      t('Il sito è stato rinnovato e alcuni indirizzi sono cambiati. Riparti da qui:', 'El sitio se ha renovado y algunas direcciones han cambiado. Empieza desde aquí:'),
                      btn(url('home'), t('Vai alla home', 'Ir a la página de inicio')) + btn(url('faq'), t('Leggi le domande frequenti', 'Lee las preguntas frecuentes'), 'o'))
    return dict(title=t('Pagina non trovata | Odyra System', 'Página no encontrada | Odyra System'), desc='', crumb='404', body=body, type='WebPage', ld=[], noindex=True)


BUILDERS = {
    'home': page_home, 'piattaforma': page_piattaforma, 'settori': page_settori, 'partner': page_partner,
    'goagent': page_goagent, 'misura': page_misura, 'chi': page_chi, 'faq': page_faq, 'contatti': page_contatti, 'privacy': page_privacy,
}
LLMS_ORDER = ['home', 'piattaforma', 'settori', 'partner', 'goagent', 'misura', 'chi', 'faq', 'contatti']


# ───────── JSON-LD ─────────
def org_node():
    return {
        '@type': 'Organization', '@id': f'{SITE}/#org', 'name': 'Odyra System', 'legalName': COMPANY['legal'],
        'url': f'{SITE}/', 'logo': f'{SITE}/assets/logos/odyra-mark.png', 'image': f'{SITE}/assets/img/og.jpg', 'email': EMAIL,
        'vatID': 'IT' + COMPANY['vat'], 'foundingLocation': 'Milano',
        'description': t('Azienda tecnologica di Milano che costruisce agenti AI di settore, voce e WhatsApp, in white-label per i software di gestione.',
                         'Empresa tecnológica de Milán que construye agentes IA sectoriales, de voz y WhatsApp, en white-label para software de gestión.'),
        'address': {'@type': 'PostalAddress', 'streetAddress': COMPANY['street'], 'postalCode': COMPANY['zip'], 'addressLocality': COMPANY['city'], 'addressRegion': 'MI', 'addressCountry': 'IT'},
        'contactPoint': {'@type': 'ContactPoint', 'contactType': 'sales', 'email': EMAIL, 'availableLanguage': ['it', 'es']},
        'knowsAbout': ['AI agents', 'Voice AI', 'WhatsApp Business API', t('Software di gestione', 'Software de gestión'), 'White-label SaaS', 'AI Act', 'GDPR'],
        'areaServed': ['IT', 'ES'],
        'owns': {'@type': 'SoftwareApplication', 'name': 'HAKO', 'url': LINK_HAKO, 'applicationCategory': 'BusinessApplication'},
    }


def jsonld(key, p):
    page_url = SITE + url(key)
    nodes = [org_node(),
             {'@type': 'WebSite', '@id': f'{SITE}/#website', 'url': f'{SITE}/', 'name': 'Odyra System', 'inLanguage': ['it-IT', 'es-ES'], 'publisher': {'@id': f'{SITE}/#org'}}]
    page = {'@type': p['type'], '@id': page_url + '#page', 'url': page_url, 'name': p['title'], 'description': p['desc'],
            'inLanguage': 'it-IT' if L == 'it' else 'es-ES', 'isPartOf': {'@id': f'{SITE}/#website'}, 'about': {'@id': f'{SITE}/#org'},
            'dateModified': UPDATED, 'primaryImageOfPage': f'{SITE}/assets/img/og.jpg'}
    if key != 'home':
        page['breadcrumb'] = {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + url('home')},
            {'@type': 'ListItem', 'position': 2, 'name': p['crumb'], 'item': page_url}]}
    if p.get('faq_main'):
        page['mainEntity'] = [{'@type': 'Question', 'name': strip(q), 'acceptedAnswer': {'@type': 'Answer', 'text': strip(a)}} for q, a in p['faq']]
    nodes.append(page)
    nodes += p.get('ld', [])
    return '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': nodes}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + '</script>'


def strip(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s))


# ───────── layout ─────────
def lang_switch(key):
    return ('<p class="lang">' + ''.join(
        f'<a href="{url(key, lg)}" hreflang="{lg}" lang="{lg}"{" aria-current=\"true\"" if lg == L else ""}>{lg.upper()}</a>' for lg in LANGS) + '</p>')


def layout(key, p):
    path = url(key) if key != '404' else ('/404.html' if L == 'it' else '/es/404.html')
    noindex = p.get('noindex')
    alts = '' if key == '404' else ''.join(f'<link rel="alternate" hreflang="{lg}" href="{SITE}{url(key, lg)}">' for lg in LANGS) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{url(key, "it")}">'
    md = '' if (noindex or key == '404') else f'<link rel="alternate" type="text/markdown" href="{md_url(key)}" title="Markdown">'
    cur = lambda k: ' aria-current="page"' if k == key else ''
    nav = ''.join(f'<a href="{url(k)}"{cur(k)}>{label}</a>' for k, label in nav_items())
    lk = key if key in PATHS else 'home'
    head = f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script>document.documentElement.classList.add('js')</script>
<title>{e(p['title'])}</title>
{f'<meta name="description" content="{e(p["desc"])}">' if p['desc'] else ''}
<meta name="robots" content="{'noindex,follow' if noindex else 'index,follow,max-snippet:-1,max-image-preview:large'}">
{'' if key == '404' else f'<link rel="canonical" href="{SITE}{path}">'}
{alts}{md}
<link rel="alternate" type="text/plain" href="/llms.txt" title="llms.txt">
<meta property="og:type" content="website"><meta property="og:site_name" content="Odyra System"><meta property="og:locale" content="{'it_IT' if L == 'it' else 'es_ES'}">
<meta property="og:title" content="{e(p['title'])}"><meta property="og:description" content="{e(p['desc'])}">
<meta property="og:url" content="{SITE}{path}"><meta property="og:image" content="{SITE}/assets/img/og.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#071A3A">
<link rel="icon" href="/assets/icons/favicon.ico" sizes="any"><link rel="icon" href="/assets/icons/fav-48.png" type="image/png" sizes="48x48"><link rel="apple-touch-icon" href="/assets/icons/fav-180.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="preload" href="/assets/fonts/schibsted-grotesk-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/styles.css?v={ASSET_V}">
{'' if key == '404' else jsonld(key, p)}'''
    crumbs = '' if key in ('home', '404') else f'<nav class="crumbs" aria-label="Breadcrumb" data-md="skip"><div class="wrap"><ol><li><a href="{url("home")}">Home</a></li><li aria-current="page">{p["crumb"]}</li></ol></div></nav>'
    return f'''<!doctype html>
<html lang="{L}">
<head>
{head}
</head>
<body>
<a class="skip" href="#main">{t('Vai al contenuto', 'Ir al contenido')}</a>
<header class="hdr"><div class="wrap hdr-in">
  <a class="brand" href="{url('home')}"><img src="/assets/logos/odyra-system.webp" alt="Odyra System" width="163" height="44"></a>
  <button class="burger" id="burger" type="button" aria-expanded="false" aria-controls="nav">{t('Menu', 'Menú')}</button>
  <nav class="nav" id="nav" aria-label="{t('Principale', 'Principal')}">{nav}{lang_switch(lk)}{btn(url('contatti'), t('Richiedi una demo', 'Solicita una demo'), 'c')}</nav>
</div></header>
{crumbs}
<main id="main">
{p['body']}
</main>
{footer()}
<script src="/script.js?v={ASSET_V}" defer></script>
</body>
</html>
'''


def footer():
    col = lambda title, items: f'<div><h2>{title}</h2><ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul></div>'
    a = lambda k: f'<a href="{url(k)}">{dict(nav_items() + [("faq", t("Domande frequenti", "Preguntas frecuentes")), ("contatti", t("Contatti", "Contacto")), ("privacy", "Privacy")])[k]}</a>'
    return f'''<footer class="ftr"><div class="wrap">
  <div class="ftr-top">
    <div class="ftr-about"><img src="/assets/logos/odyra-system.webp" alt="Odyra System" width="163" height="44" loading="lazy">
      <p>{t('Agenti AI di settore, in white-label per i software di gestione. Milano.', 'Agentes IA sectoriales, en white-label para software de gestión. Milán.')}</p></div>
    {col('Odyra', [a('piattaforma'), a('settori'), a('partner'), a('misura'), a('chi')])}
    {col(t('Costruito con Odyra', 'Construido con Odyra'), [a('goagent'), f'<a href="{LINK_HAKO}" rel="noopener">HAKO</a>'])}
    {col(t('Risorse', 'Recursos'), [a('faq'), a('contatti'), '<a href="/llms.txt">llms.txt</a>'])}
  </div>
  <p class="ftr-legal">© 2026 Odyra System, {COMPANY['legal']}. {t('Partita IVA', 'NIF-IVA')} {COMPANY['vat']}, REA {COMPANY['rea']}. {COMPANY['street']}, {COMPANY['zip']} {COMPANY['city']}. {a('privacy')}</p>
</div></footer>'''


# ───────── HTML → Markdown (per /pagina.md e llms-full.txt) ─────────
class MD(HTMLParser):
    VOID = {'br', 'img', 'input', 'meta', 'link', 'hr', 'source', 'track', 'wbr'}
    SKIP = {'script', 'style', 'form', 'button', 'svg', 'video', 'select', 'textarea'}
    BLOCKS = {'p', 'div', 'section', 'figure', 'figcaption', 'aside', 'details', 'summary', 'header', 'dl'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.buf, self.pre, self.skip, self.lists, self.links = [], '', '', 0, [], []

    def flush(self, gap=False):
        s = re.sub(r'\s+', ' ', self.buf).strip()
        if s:
            self.out.append(self.pre + s)
            self.pre = ''
            if gap and not self.lists:
                self.out.append('')
        self.buf = ''

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.skip:
            self.skip += tag not in self.VOID
            return
        if a.get('data-md') == 'skip' or tag in self.SKIP:
            self.skip = int(tag not in self.VOID)
            return
        if tag in ('ul', 'ol'):
            self.flush()
            self.lists.append([tag, 0])
        elif tag == 'li':
            self.flush()
            lst = self.lists[-1]
            lst[1] += 1
            self.pre = '  ' * (len(self.lists) - 1) + (f'{lst[1]}. ' if lst[0] == 'ol' else '- ')
        elif tag in ('h1', 'h2', 'h3', 'h4'):
            self.flush(True)
            self.pre = '#' * int(tag[1]) + ' '
        elif tag == 'dt':
            self.flush()
            self.pre = '- '
            self.buf = '**'
        elif tag in self.BLOCKS:
            self.flush(True)
        elif tag in ('b', 'strong'):
            self.buf += '**'
        elif tag == 'a':
            self.links.append((len(self.buf), a.get('href', '')))
            self.buf += '['
        elif tag == 'img' and a.get('alt'):
            self.buf += f'![{a["alt"]}]({abs_url(a.get("src", ""))})'
        elif tag == 'br':
            self.buf += ' '

    def handle_endtag(self, tag):
        if self.skip:
            self.skip -= tag not in self.VOID
            return
        if tag in ('ul', 'ol'):
            self.flush()
            self.lists.pop()
            if not self.lists:
                self.out.append('')
        elif tag == 'li':
            self.flush()
        elif tag in ('h1', 'h2', 'h3', 'h4'):
            self.flush()
            self.out.append('')
        elif tag == 'dt':
            self.buf = self.buf.rstrip() + '**: '
        elif tag == 'dd':
            self.flush()
        elif tag == 'dl':
            self.flush()
            self.out.append('')
        elif tag in ('b', 'strong'):
            self.buf = self.buf.rstrip() + '** '
        elif tag == 'a' and self.links:
            i, href = self.links.pop()
            if href and not href.startswith('#'):
                self.buf = self.buf.rstrip() + f']({abs_url(href)}) '
            else:
                self.buf = self.buf[:i] + self.buf[i + 1:]
        elif tag in self.BLOCKS:
            self.flush(True)

    def handle_data(self, data):
        if not self.skip:
            self.buf += data


def abs_url(h):
    if h.startswith('/'):
        return SITE + h
    return h


def to_markdown(key, p):
    m = re.search(r'<main id="main">(.*)</main>', layout(key, p), re.S)
    parser = MD()
    parser.feed(m.group(1))
    parser.flush()
    text = '\n'.join(parser.out)
    text = re.sub(r'\*\*\s*\*\*', '', text)
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    meta = f'> {p["desc"]}\n\n' + t('Fonte', 'Fuente') + f': {SITE}{url(key)} · ' + t('Aggiornato il', 'Actualizado el') + f' {UPDATED}\n\n'
    # Il titolo H1 è già nel corpo: metadati subito dopo la prima riga.
    first, _, rest = text.partition('\n')
    return f'{first}\n\n{meta}{rest.strip()}\n'


# ───────── scrittura ─────────
ASSET_V = '1'


def write(rel, content):
    path = os.path.join(DIST, rel.lstrip('/'))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def asset_version():
    import hashlib
    h = hashlib.sha1()
    for n in ('styles.css', 'script.js'):
        with open(os.path.join(STATIC, n), 'rb') as f:
            h.update(f.read())
    return h.hexdigest()[:8]


def llms_txt(pages_by_lang, full=False):
    global L
    if full:
        parts = []
        for lg in LANGS:
            L = lg
            for k in LLMS_ORDER:
                parts.append(pages_by_lang[lg][k]['md'])
        L = 'it'
        head = ('# Odyra System: testo completo del sito / texto completo del sitio\n\n'
                f'> Tutte le pagine pubbliche di {SITE} in Markdown, in italiano e in spagnolo. Aggiornato il {UPDATED}.\n\n')
        return head + '\n\n---\n\n'.join(parts)
    L = 'it'
    out = ['# Odyra System', '',
           '> Odyra System è un’azienda tecnologica di Milano (Verypos S.r.l.) che costruisce agenti AI di settore: rispondono al telefono e su WhatsApp, prenotano e gestiscono appuntamenti seguendo le regole di un settore preciso. Li collega ai software di gestione, che li offrono ai loro clienti in white-label, con il proprio marchio.', '',
           'Fatti chiave:', '',
           '- In produzione nel settore beauty con GoAgent, il servizio AI di BOSS per gli oltre 1.500 saloni che usano il gestionale GoWeb, da giugno 2026.',
           '- Canali: telefono (voce in tempo reale) e WhatsApp Business. Odyra è Tech Provider Meta tramite Vonage.',
           '- Le regole del settore sono scritte nel codice; l’agente legge e scrive nel software di gestione e dice sempre di essere un’AI (AI Act).',
           '- Modello: white-label con canone ricorrente per cliente e revenue condivisa con il software partner; Odyra gestisce connettore, onboarding, qualità e assistenza.',
           '- Altri prodotti: HAKO, software proprietario per le portinerie dei condomini (https://hakocondomini.com). Progetti su misura per aziende con grandi volumi (es. Gruppo Colzani).',
           f'- Contatti: {EMAIL}, {COMPANY["street"]}, {COMPANY["zip"]} {COMPANY["city"]}, Italia.', '',
           'Ogni pagina ha una versione Markdown allo stesso indirizzo con estensione .md. Il testo completo è in /llms-full.txt.', '',
           '## Pagine (italiano)', '']
    for k in LLMS_ORDER:
        p = pages_by_lang['it'][k]
        out.append(f'- [{p["crumb"]}]({SITE}{md_url(k, "it")}): {p["desc"]}')
    out += ['', '## Páginas (español)', '']
    L = 'es'
    for k in LLMS_ORDER:
        p = pages_by_lang['es'][k]
        out.append(f'- [{p["crumb"]}]({SITE}{md_url(k, "es")}): {p["desc"]}')
    L = 'it'
    out += ['', '## Optional', '', f'- [Testo completo / Texto completo]({SITE}/llms-full.txt): tutte le pagine in un unico file.',
            f'- [Sitemap]({SITE}/sitemap.xml)', '']
    return '\n'.join(out)


def sitemap(keys):
    rows = []
    for k in keys:
        for lg in LANGS:
            alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{l2}" href="{SITE}{url(k, l2)}"/>' for l2 in LANGS)
            alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{url(k, "it")}"/>'
            pr = '1.0' if k == 'home' else '0.8'
            rows.append(f'<url><loc>{SITE}{url(k, lg)}</loc><lastmod>{UPDATED}</lastmod><priority>{pr}</priority>{alts}</url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + '\n'.join(rows) + '\n</urlset>\n')


ROBOTS = f'''# Odyra System. Tutti i contenuti pubblici sono aperti ai motori di ricerca e agli assistenti AI.
# Versione per modelli linguistici: {SITE}/llms.txt (testo completo: {SITE}/llms-full.txt)

User-agent: *
Allow: /

# Assistenti e motori di ricerca AI: accesso esplicito.
User-agent: GPTBot
User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: ClaudeBot
User-agent: Claude-SearchBot
User-agent: Claude-User
User-agent: anthropic-ai
User-agent: PerplexityBot
User-agent: Perplexity-User
User-agent: Google-Extended
User-agent: GoogleOther
User-agent: Applebot
User-agent: Applebot-Extended
User-agent: Bingbot
User-agent: DuckAssistBot
User-agent: MistralAI-User
User-agent: Meta-ExternalAgent
User-agent: meta-externalfetcher
User-agent: Amazonbot
User-agent: cohere-ai
User-agent: CCBot
Allow: /

Sitemap: {SITE}/sitemap.xml
'''

MANIFEST = json.dumps({'name': 'Odyra System', 'short_name': 'Odyra', 'start_url': '/', 'display': 'standalone',
                       'background_color': '#071A3A', 'theme_color': '#071A3A',
                       'icons': [{'src': '/assets/icons/fav-192.png', 'sizes': '192x192', 'type': 'image/png'},
                                 {'src': '/assets/icons/fav-512.png', 'sizes': '512x512', 'type': 'image/png'}]})


def main():
    global L, ASSET_V
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    shutil.copytree(STATIC, DIST)
    ASSET_V = asset_version()
    pages = {}
    for lg in LANGS:
        L = lg
        pages[lg] = {}
        base = '' if lg == 'it' else 'es/'
        for k, fn in BUILDERS.items():
            p = fn()
            html_out = layout(k, p)
            p['md'] = to_markdown(k, p)
            pages[lg][k] = p
            path = PATHS[k][LANGS.index(lg)]
            write(f'{base}{path + "/" if path else ""}index.html', html_out)
            if not p.get('noindex'):
                write(md_url(k), p['md'])
        write(f'{base}404.html', layout('404', page_404()))
    L = 'it'
    write('llms.txt', llms_txt(pages))
    write('llms-full.txt', llms_txt(pages, full=True))
    write('sitemap.xml', sitemap([k for k in BUILDERS if k != 'privacy']))
    write('robots.txt', ROBOTS)
    write('manifest.webmanifest', MANIFEST)
    n = sum(len(v) for v in pages.values())
    print(f'Generate {n} pagine in {DIST}')


if __name__ == '__main__':
    main()
