#!/usr/bin/env python3
"""Genera il sito Odyra System in dist/: italiano in radice, spagnolo in /es/, stesso design.

Uso: python3 build.py

Le pagine stanno in pagine/ (italiano) e pagine/es/ (spagnolo), solo il contenuto di <main>.
Da qui escono, per ogni pagina: HTML statico con testata, piede e <head>, versione Markdown
(/pagina.md), dati strutturati JSON-LD. Per tutto il sito: llms.txt, llms-full.txt, sitemap.xml,
robots.txt. Solo libreria standard di Python.
"""
import hashlib
import html
import json
import os
import re
import shutil
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(ROOT, 'static')
DIST = os.path.join(ROOT, 'dist')
PAGINE = os.path.join(ROOT, 'pagine')

SITE = 'https://odyrasystemautomation.it'
EMAIL = 'team@odyrasystemautomation.it'
UPDATED = '2026-10-22'  # data dell'ultimo aggiornamento dei contenuti (sitemap, JSON-LD)
LINK_HAKO = 'https://hakocondomini.com'
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
# chiave, sorgente in pagine/ e pagine/es/ (None = generata qui), voce di menu
PAGES = [
    ('home', 'home.html', False),
    ('soluzioni', 'soluzioni.html', True),
    ('agenti', 'agenti.html', True),
    ('piattaforma', 'piattaforma.html', True),
    ('academy', 'academy.html', True),
    ('casi', 'casi.html', True),
    ('chi', 'chi-siamo.html', True),
    ('contatti', 'contatti.html', False),
    ('domande', None, False),
    ('privacy', None, False),
]
NOINDEX = ('privacy',)

# per lingua: indirizzo, etichetta (menu e briciole), titolo, descrizione
TEXT = {
    'it': {
        'home': ('', 'Home', 'Odyra System: agenti AI su scala, col vostro marchio',
                 'Odyra progetta e gestisce agenti AI white-label per aziende con centinaia o migliaia di sedi, clienti e punti vendita: voce, WhatsApp, prenotazioni, vendite e assistenza.'),
        'soluzioni': ('soluzioni', 'Soluzioni', 'Soluzioni per software house, aziende, reti e agenzie | Odyra',
                      'Come Odyra lavora con software house, grandi aziende, franchising e agenzie: agenti AI col loro marchio, gestiti da Odyra.'),
        'agenti': ('agenti', 'Agenti', 'Agenti AI e servizi | Odyra',
                   'Il catalogo degli agenti AI e dei servizi Odyra: voce, messaggi, vendite, assistenza, operazioni, qualità e infrastruttura.'),
        'piattaforma': ('piattaforma', 'Piattaforma', 'La piattaforma | Odyra',
                        'Come è fatta la piattaforma Odyra: un solo cervello condiviso, regole di settore nel codice, connettori ai sistemi del cliente.'),
        'academy': ('academy', 'Academy', 'Odyra Academy: consulenza e formazione sull’AI | Odyra',
                    'Workshop, webinar, percorsi per i team e consulenza sull’intelligenza artificiale per le aziende, da chi mette agenti AI in produzione.'),
        'casi': ('casi', 'Casi di successo', 'Casi di successo | Odyra',
                 'BOSS, HAKO e Gruppo Colzani: agenti Odyra al lavoro.'),
        'chi': ('chi-siamo', 'Chi siamo', 'Chi siamo | Odyra',
                'Odyra System, gruppo tecnologico di Milano: chi siamo, metodo, missione e visione.'),
        'contatti': ('contatti', 'Contatti', 'Contatti | Odyra',
                     'Richiedi una demo di un agente AI Odyra o un workshop dell’Academy.'),
        'domande': ('domande', 'Domande frequenti', 'Domande frequenti su Odyra System e gli agenti AI',
                    'Risposte su Odyra System: agenti AI di settore, canali, software supportati, white-label, GDPR, AI Act e WhatsApp Business.'),
        'privacy': ('privacy', 'Privacy', 'Informativa privacy | Odyra System',
                    'Informativa sul trattamento dei dati personali del sito Odyra System.'),
    },
    'es': {
        'home': ('', 'Inicio', 'Odyra System: agentes IA a escala, con vuestra marca',
                 'Odyra diseña y gestiona agentes IA white-label para empresas con cientos o miles de sedes, clientes y puntos de venta: voz, WhatsApp, reservas, ventas y atención al cliente.'),
        'soluzioni': ('soluciones', 'Soluciones', 'Soluciones para empresas de software, grandes empresas, redes y agencias | Odyra',
                      'Cómo trabaja Odyra con empresas de software, grandes empresas, franquicias y agencias: agentes IA con su marca, gestionados por Odyra.'),
        'agenti': ('agentes', 'Agentes', 'Agentes IA y servicios | Odyra',
                   'El catálogo de agentes IA y servicios de Odyra: voz, mensajes, ventas, atención, operaciones, calidad e infraestructura.'),
        'piattaforma': ('plataforma', 'Plataforma', 'La plataforma | Odyra',
                        'Cómo está hecha la plataforma Odyra: un único cerebro compartido, reglas del sector en el código, conectores con los sistemas del cliente.'),
        'academy': ('academy', 'Academy', 'Odyra Academy: consultoría y formación en IA | Odyra',
                    'Talleres, webinars, itinerarios para equipos y consultoría sobre inteligencia artificial para empresas, de quien pone agentes IA en producción.'),
        'casi': ('casos', 'Casos de éxito', 'Casos de éxito | Odyra',
                 'BOSS, HAKO y Gruppo Colzani: agentes Odyra trabajando.'),
        'chi': ('quienes-somos', 'Quiénes somos', 'Quiénes somos | Odyra',
                'Odyra System, grupo tecnológico de Milán: quiénes somos, método, misión y visión.'),
        'contatti': ('contacto', 'Contacto', 'Contacto | Odyra',
                     'Solicita una demo de un agente IA de Odyra o un taller de la Academy.'),
        'domande': ('preguntas', 'Preguntas frecuentes', 'Preguntas frecuentes sobre Odyra System y los agentes IA',
                    'Respuestas sobre Odyra System: agentes IA sectoriales, canales, software compatible, white-label, RGPD, AI Act y WhatsApp Business.'),
        'privacy': ('privacidad', 'Privacidad', 'Política de privacidad | Odyra System',
                    'Política de tratamiento de datos personales del sitio Odyra System.'),
    },
}

# testi fissi di testata, piede e pagine generate
UI = {
    'it': dict(skip='Vai al contenuto', menu='Menu', nav='Principale', demo='Richiedi una demo', other='ES', other_name='Español',
               about='La fabbrica di agenti AI white-label. Milano, per l’Italia e la Spagna.',
               solutions='Soluzioni', resources='Risorse', sw='Software house', big='Grandi aziende', fr='Franchising e reti', ag='Agenzie e integratori',
               agents='Agenti e servizi', vat='Partita IVA', source='Fonte', updated='Aggiornato il',
               faq_lead='Agenti AI di settore, canali, software supportati, white-label, dati e AI Act: le risposte in breve.',
               faq_more='Non trovi la risposta? <a href="{c}">Scrivici</a>: rispondiamo entro un giorno lavorativo.',
               nf_title='Pagina non trovata', nf_lead='L’indirizzo non esiste o è stato spostato. Riparti dalla <a href="{h}">home</a> o <a href="{c}">scrivici</a>.',
               privacy_h1='Informativa sulla privacy.', privacy_lead='Come trattiamo i dati raccolti da questo sito.'),
    'es': dict(skip='Ir al contenido', menu='Menú', nav='Principal', demo='Solicita una demo', other='IT', other_name='Italiano',
               about='La fábrica de agentes IA white-label. Milán, para Italia y España.',
               solutions='Soluciones', resources='Recursos', sw='Empresas de software', big='Grandes empresas', fr='Franquicias y redes', ag='Agencias e integradores',
               agents='Agentes y servicios', vat='NIF-IVA', source='Fuente', updated='Actualizado el',
               faq_lead='Agentes IA sectoriales, canales, software compatible, white-label, datos y AI Act: las respuestas en breve.',
               faq_more='¿No encuentras la respuesta? <a href="{c}">Escríbenos</a>: respondemos en un día laborable.',
               nf_title='Página no encontrada', nf_lead='La dirección no existe o se ha movido. Vuelve al <a href="{h}">inicio</a> o <a href="{c}">escríbenos</a>.',
               privacy_h1='Política de privacidad.', privacy_lead='Cómo tratamos los datos que recoge este sitio.'),
}

CATS = {
    'it': [('voce', 'Voce', 'Agenti che parlano al telefono, in entrata e in uscita, e dal vostro sito.'),
           ('messaggi', 'Messaggi', 'WhatsApp, promemoria, recensioni, in più lingue.'),
           ('vendite', 'Vendite', 'Lead, ordini, solleciti: gli agenti che portano e difendono il fatturato.'),
           ('assistenza', 'Assistenza', 'Clienti e dipendenti con una risposta giusta, a qualsiasi ora.'),
           ('operazioni', 'Operazioni', 'Il lavoro ripetitivo dietro le quinte: documenti, dati, flussi.'),
           ('qualita', 'Qualità e dati', 'Gli agenti che controllano gli altri agenti, e i report per chi decide.'),
           ('infrastruttura', 'Infrastruttura', 'Dove gira l’AI e come si collega ai vostri sistemi.')],
    'es': [('voce', 'Voz', 'Agentes que hablan por teléfono, en llamadas entrantes y salientes, y desde vuestra web.'),
           ('messaggi', 'Mensajes', 'WhatsApp, recordatorios, reseñas, en varios idiomas.'),
           ('vendite', 'Ventas', 'Leads, pedidos, reclamaciones de pago: los agentes que traen y defienden la facturación.'),
           ('assistenza', 'Atención', 'Clientes y empleados con la respuesta correcta, a cualquier hora.'),
           ('operazioni', 'Operaciones', 'El trabajo repetitivo entre bastidores: documentos, datos, flujos.'),
           ('qualita', 'Calidad y datos', 'Los agentes que controlan a los demás agentes, y los informes para quien decide.'),
           ('infrastruttura', 'Infraestructura', 'Dónde funciona la IA y cómo se conecta con vuestros sistemas.')],
}


def base(lang):
    return '/' if lang == 'it' else '/es/'


def path(key, lang):
    slug = TEXT[lang][key][0]
    return base(lang) + (slug + '/' if slug else '')


def md_path(key, lang):
    return base(lang) + (TEXT[lang][key][0] or 'index') + '.md'


# ───────── domande frequenti (pagina /domande/ e /es/preguntas/) ─────────
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


# ───────── JSON-LD ─────────
def og_image(lang):
    return f"{SITE}/assets/img/{'og.jpg' if lang == 'it' else 'og-es.jpg'}"
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


def strip(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s))


# ───────── corpi delle pagine ─────────
def without_placeholders(body):
    """Toglie i riquadri per foto, video e premi non ancora disponibili: in pagine/ restano, sul sito non si vedono.
    Per pubblicarne uno basta sostituire il riquadro con il contenuto vero e rigenerare."""
    drop_if = lambda marker: (lambda m: '' if marker in m.group(0) else m.group(0))
    body = re.sub(r'(<!--[^>]*-->\s*)?<section class="film[^"]*">.*?</section>', drop_if('slot-box'), body, flags=re.S)
    body = re.sub(r'<div class="photo-strip[^"]*"[^>]*>.*?</ol></div>', drop_if('slot-mini'), body, flags=re.S)
    body = re.sub(r'<figure class="slot[^"]*">\s*<div class="slot-box"[^>]*>.*?</div>\s*</figure>', '', body, flags=re.S)
    body = re.sub(r'<section class="team paper">\s*<div class="wrap">\s*<h2>.*?</section>', drop_if('person-photo'), body, flags=re.S)
    body = re.sub(r'<li class="partner-slot">.*?</li>', '', body, flags=re.S)
    return body


def phead(lang, crumb, h1, lead):
    return f'''<section class="phead ink">
  <canvas class="hero-guilloche" aria-hidden="true"></canvas>
  <div class="wrap phead-in">
    <p class="crumbs" data-md="skip"><a href="{base(lang)}">{TEXT[lang]['home'][1]}</a> <span aria-hidden="true">/</span> {crumb}</p>
    <h1 class="display">{h1}</h1>
    <p class="hero-lead">{lead}</p>
  </div>
</section>'''


def body_domande(lang):
    u = UI[lang]
    qa = ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in faq_all())
    return phead(lang, TEXT[lang]['domande'][1], TEXT[lang]['domande'][1] + '.', u['faq_lead']) + f'''
<section class="qa paper">
  <div class="wrap">
    <div class="qa-list">{qa}</div>
    <p class="sec-lead">{u['faq_more'].format(c=path('contatti', lang))}</p>
  </div>
</section>'''


def body_privacy(lang):
    u = UI[lang]
    # Bozza: da far rivedere a un legale prima di considerarla definitiva.
    return phead(lang, TEXT[lang]['privacy'][1], u['privacy_h1'], u['privacy_lead']) + f'''
<section class="paper">
  <div class="wrap prose">
    <h2>{t('Titolare del trattamento', 'Responsable del tratamiento')}</h2>
    <p>{COMPANY['legal']}, {COMPANY['street']}, {COMPANY['zip']} {t('Milano', 'Milán')}. {u['vat']} {COMPANY['vat']}. <a href="mailto:{EMAIL}">{EMAIL}</a></p>
    <h2>{t('Dati raccolti', 'Datos recogidos')}</h2>
    <p>{t('Con il modulo contatti raccogliamo nome, azienda, e-mail, telefono e messaggio, al solo scopo di rispondere alla tua richiesta. Li conserviamo per il tempo necessario a gestirla.', 'Con el formulario de contacto recogemos nombre, empresa, correo, teléfono y mensaje, solo para responder a tu solicitud. Los conservamos el tiempo necesario para gestionarla.')}</p>
    <h2>{t('Cookie e servizi esterni', 'Cookies y servicios externos')}</h2>
    <p>{t('Il sito non usa cookie di profilazione né strumenti di tracciamento. Caratteri e librerie sono ospitati sul nostro server: nessun dato viene inviato a servizi di terzi per visualizzare le pagine.', 'El sitio no usa cookies de perfilado ni herramientas de seguimiento. Las fuentes y librerías están alojadas en nuestro servidor: no se envía ningún dato a terceros para mostrar las páginas.')}</p>
    <h2>{t('I tuoi diritti', 'Tus derechos')}</h2>
    <p>{t(f'Puoi chiedere accesso, rettifica, cancellazione e opposizione scrivendo a <a href="mailto:{EMAIL}">{EMAIL}</a>. Puoi anche presentare reclamo al Garante per la protezione dei dati personali.', f'Puedes pedir acceso, rectificación, supresión y oposición escribiendo a <a href="mailto:{EMAIL}">{EMAIL}</a>. También puedes presentar una reclamación ante la autoridad de protección de datos.')}</p>
  </div>
</section>'''


def bodies(lang):
    """Corpo HTML di ogni pagina della lingua, con i segnaposti già sostituiti."""
    src_dir = PAGINE if lang == 'it' else os.path.join(PAGINE, 'es')
    with open(os.path.join(src_dir, 'agents.json'), encoding='utf-8') as f:
        cards = json.load(f)
    grid = ''
    for key, name, intro in CATS[lang]:
        mine = [c for c in cards if f'data-cat="{key}"' in c]
        grid += f'''<section class="cat" id="{key}"><div class="wrap">
  <header class="cat-h"><h2>{name}</h2><p>{intro}</p><span class="cat-n">{len(mine)}</span></header>
  <ol class="agents-grid">{''.join(mine)}</ol>
</div></section>
'''
    out = {}
    for key, src, _ in PAGES:
        if src:
            with open(os.path.join(src_dir, src), encoding='utf-8') as f:
                body = f.read()
            body = body.replace('{{AGENTS_N}}', str(len(cards))).replace('{{AGENTS}}', ''.join(cards)).replace('{{AGENTS_GRID}}', grid).replace('{{P}}', base(lang))
            body = without_placeholders(body)
            if re.search(r'slot-mini|slot-box|partner-slot', body):
                print(f'Attenzione: in {os.path.relpath(src_dir, ROOT)}/{src} è rimasto un segnaposto da riempire')
        else:
            body = body_domande(lang) if key == 'domande' else body_privacy(lang)
        # le briciole di pane sono già nel JSON-LD: fuori dal Markdown
        out[key] = body.replace('<p class="crumbs">', '<p class="crumbs" data-md="skip">').strip()
    return out


# ───────── testata, piede, <head> ─────────
def header(lang, current):
    u = UI[lang]
    links = ''.join(f'<a href="{path(k, lang)}"{" aria-current=\"page\"" if k == current else ""}>{TEXT[lang][k][1]}</a>' for k, _, nav in PAGES if nav)
    other = 'es' if lang == 'it' else 'it'
    return f'''<header class="top">
  <a class="top-brand" href="{base(lang)}"><img src="/assets/logos/odyra-system.webp" alt="Odyra System" width="150" height="40"></a>
  <nav class="top-nav" id="nav" aria-label="{u['nav']}">
    {links}
    <a href="{path(current or 'home', other)}" hreflang="{other}" lang="{other}" title="{u['other_name']}">{u['other']}</a>
    <a class="b b-cyan" href="{path('contatti', lang)}">{u['demo']}</a>
  </nav>
  <button class="top-menu" id="menu" type="button" aria-expanded="false" aria-controls="nav">{u['menu']}</button>
</header>'''


def footer(lang):
    u = UI[lang]
    p = lambda k: path(k, lang)
    lab = lambda k: TEXT[lang][k][1]
    col = lambda title, items: f'<div><h2>{title}</h2><ul>' + ''.join(f'<li><a href="{h}">{l}</a></li>' for l, h in items) + '</ul></div>'
    other = 'es' if lang == 'it' else 'it'
    return f'''<footer class="foot ink">
  <div class="wrap">
    <div class="foot-cols">
      <div class="foot-about"><img src="/assets/logos/odyra-system.webp" alt="Odyra System" width="150" height="40" loading="lazy"><p>{u['about']}</p></div>
      {col(u['solutions'], [(u['sw'], p('soluzioni') + '#software-house'), (u['big'], p('soluzioni') + '#grandi-aziende'), (u['fr'], p('soluzioni') + '#franchising'), (u['ag'], p('soluzioni') + '#agenzie')])}
      {col('Odyra', [(u['agents'], p('agenti')), (lab('piattaforma'), p('piattaforma')), ('Odyra Academy', p('academy')), (lab('casi'), p('casi')), (lab('chi'), p('chi'))])}
      {col(u['resources'], [(u['demo'], p('contatti')), (lab('domande'), p('domande')), (EMAIL, f'mailto:{EMAIL}'), (lab('privacy'), p('privacy')), ('llms.txt', '/llms.txt'), (u['other_name'], base(other))])}
    </div>
    <p class="foot-legal">© 2026 Odyra System, {COMPANY['legal']}, {COMPANY['street']}, {COMPANY['zip']} {t('Milano', 'Milán')}. {u['vat']} {COMPANY['vat']}, REA {COMPANY['rea']}.</p>
  </div>
</footer>'''


def qa_pairs(body):
    """Domande e risposte di una pagina (<details><summary>), per il JSON-LD FAQPage."""
    return [(strip(q), strip(a)) for q, a in re.findall(r'<details><summary>(.*?)</summary>(.*?)</details>', body, re.S)]


def jsonld(lang, key, body):
    _, label, title, desc = TEXT[lang][key]
    page_url = SITE + path(key, lang)
    page = {'@type': {'chi': 'AboutPage', 'contatti': 'ContactPage', 'domande': 'FAQPage'}.get(key, 'WebPage'),
            '@id': page_url + '#page', 'url': page_url, 'name': title, 'description': desc,
            'inLanguage': 'it-IT' if lang == 'it' else 'es-ES',
            'isPartOf': {'@id': f'{SITE}/#website'}, 'about': {'@id': f'{SITE}/#org'},
            'dateModified': UPDATED, 'primaryImageOfPage': og_image(lang)}
    if key != 'home':
        page['breadcrumb'] = {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': TEXT[lang]['home'][1], 'item': SITE + base(lang)},
            {'@type': 'ListItem', 'position': 2, 'name': label, 'item': page_url}]}
    if key == 'domande':
        page['mainEntity'] = [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in qa_pairs(body)]
    nodes = [org_node(),
             {'@type': 'WebSite', '@id': f'{SITE}/#website', 'url': f'{SITE}/', 'name': 'Odyra System', 'inLanguage': ['it-IT', 'es-ES'], 'publisher': {'@id': f'{SITE}/#org'}},
             page]
    return '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': nodes}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + '</script>'


def layout(lang, key, body, title=None, desc=None, not_found=False):
    _, _, page_title, page_desc = TEXT[lang][key]
    title, desc = title or page_title, desc or page_desc
    u = UI[lang]
    if not_found:
        seo = '<meta name="robots" content="noindex,follow">'
    else:
        url = SITE + path(key, lang)
        noindex = key in NOINDEX
        alts = ''.join(f'<link rel="alternate" hreflang="{lg}" href="{SITE}{path(key, lg)}">' for lg in LANGS) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{path(key, "it")}">'
        md = '' if noindex else f'<link rel="alternate" type="text/markdown" href="{md_path(key, lang)}" title="Markdown">'
        seo = f'''<meta name="robots" content="{'noindex,follow' if noindex else 'index,follow,max-snippet:-1,max-image-preview:large'}">
<link rel="canonical" href="{url}">
{alts}{md}
<link rel="alternate" type="text/plain" href="/llms.txt" title="llms.txt">
<meta property="og:type" content="website"><meta property="og:site_name" content="Odyra System"><meta property="og:locale" content="{'it_IT' if lang == 'it' else 'es_ES'}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{og_image(lang)}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
{jsonld(lang, key, body)}'''
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script>document.documentElement.classList.add('js')</script>
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{seo}
<meta name="theme-color" content="#071A3A">
<link rel="icon" href="/assets/icons/favicon.ico" sizes="any"><link rel="icon" href="/assets/icons/fav-48.png" type="image/png" sizes="48x48"><link rel="apple-touch-icon" href="/assets/icons/fav-180.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="preload" href="/assets/fonts/archivo-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/odyra.css?v={ASSET_V}">
<script src="/assets/vendor/gsap.min.js" defer></script>
<script src="/assets/vendor/ScrollTrigger.min.js" defer></script>
<script src="/assets/vendor/SplitText.min.js" defer></script>
<script src="/odyra.js?v={ASSET_V}" defer></script>
</head>
<body>
<a class="skip" href="#main">{u['skip']}</a>
{header(lang, None if not_found else key)}
<main id="main">
{body}
</main>
{footer(lang)}
</body>
</html>
'''


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


def to_markdown(lang, key, body):
    _, _, title, desc = TEXT[lang][key]
    u = UI[lang]
    parser = MD()
    parser.feed(body)
    parser.flush()
    text = '\n'.join(parser.out)
    text = re.sub(r'\*\*\s*\*\*', '', text)
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    if not text.startswith('# '):
        text = f'# {title}\n\n{text}'
    first, _, rest = text.partition('\n')
    return f'{first}\n\n> {desc}\n\n{u["source"]}: {SITE}{path(key, lang)} · {u["updated"]} {UPDATED}\n\n{rest.strip()}\n'


# ───────── scrittura ─────────
ASSET_V = '1'


def write(rel, content):
    dest = os.path.join(DIST, rel.lstrip('/'))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(content)


def asset_version(*names):
    h = hashlib.sha1()
    for n in names:
        with open(os.path.join(STATIC, n), 'rb') as f:
            h.update(f.read())
    return h.hexdigest()[:8]


def llms_txt(mds, full=False):
    pages = [k for k, _, _ in PAGES if k not in NOINDEX]
    if full:
        head = ('# Odyra System: testo completo del sito / texto completo del sitio\n\n'
                f'> Tutte le pagine pubbliche di {SITE} in Markdown, in italiano e in spagnolo. Aggiornato il {UPDATED}.\n\n')
        return head + '\n\n---\n\n'.join(mds[lg][k] for lg in LANGS for k in pages)
    out = ['# Odyra System', '',
           '> Odyra System è un gruppo tecnologico di Milano (Verypos S.r.l.) che progetta e gestisce agenti AI white-label: sistemi di agenti per aziende con centinaia o migliaia di sedi, clienti e punti vendita, venduti e usati col marchio del cliente.', '',
           'Fatti chiave:', '',
           '- Agenti per voce (telefono in tempo reale), WhatsApp Business ed e-mail: prenotazioni, vendite, assistenza, operazioni e controllo qualità.',
           '- In produzione nel settore beauty con GoAgent, il servizio AI di BOSS per gli oltre 1.500 saloni che usano il gestionale GoWeb, da giugno 2026.',
           '- Modello white-label: Odyra costruisce e gestisce l’agente (connettori, onboarding, qualità, assistenza), il cliente lo offre col proprio marchio.',
           '- Clienti: software house, grandi aziende, franchising e reti, agenzie e integratori. Odyra è Tech Provider Meta tramite Vonage.',
           '- L’agente dice sempre di essere un’AI (AI Act); dati isolati per cliente, conforme al GDPR.',
           '- Altri prodotti e servizi: HAKO, software proprietario per le portinerie dei condomini (https://hakocondomini.com); progetti su misura (es. Gruppo Colzani); Odyra Academy, consulenza e formazione sull’AI.',
           f'- Contatti: {EMAIL}, {COMPANY["street"]}, {COMPANY["zip"]} {COMPANY["city"]}, Italia.', '',
           'Ogni pagina ha una versione Markdown allo stesso indirizzo con estensione .md. Il testo completo è in /llms-full.txt.', '']
    for lg, title in (('it', '## Pagine (italiano)'), ('es', '## Páginas (español)')):
        out += [title, '']
        out += [f'- [{TEXT[lg][k][1]}]({SITE}{md_path(k, lg)}): {TEXT[lg][k][3]}' for k in pages]
        out.append('')
    out += ['## Optional', '', f'- [Testo completo / Texto completo]({SITE}/llms-full.txt): tutte le pagine in un unico file.',
            f'- [Sitemap]({SITE}/sitemap.xml)', '']
    return '\n'.join(out)


def sitemap():
    rows = []
    for k, _, _ in PAGES:
        if k in NOINDEX:
            continue
        alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{lg}" href="{SITE}{path(k, lg)}"/>' for lg in LANGS)
        alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{path(k, "it")}"/>'
        for lg in LANGS:
            rows.append(f'<url><loc>{SITE}{path(k, lg)}</loc><lastmod>{UPDATED}</lastmod><priority>{"1.0" if k == "home" else "0.8"}</priority>{alts}</url>')
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
    ASSET_V = asset_version('odyra.css', 'odyra.js')
    mds = {}
    for lang in LANGS:
        L = lang
        mds[lang] = {}
        for key, body in bodies(lang).items():
            slug = TEXT[lang][key][0]
            write(f'{base(lang)}{slug + "/" if slug else ""}index.html', layout(lang, key, body))
            if key not in NOINDEX:
                mds[lang][key] = to_markdown(lang, key, body)
                write(md_path(key, lang), mds[lang][key])
        u = UI[lang]
        nf = phead(lang, u['nf_title'], u['nf_title'] + '.', u['nf_lead'].format(h=base(lang), c=path('contatti', lang)))
        write(f'{base(lang)}404.html', layout(lang, 'home', nf, title=f"{u['nf_title']} | Odyra System", desc=u['nf_title'] + '.', not_found=True))
    L = 'it'
    write('llms.txt', llms_txt(mds))
    write('llms-full.txt', llms_txt(mds, full=True))
    write('sitemap.xml', sitemap())
    write('robots.txt', ROBOTS)
    write('manifest.webmanifest', MANIFEST)
    print(f'Generate {sum(len(v) for v in mds.values())} pagine indicizzabili ({", ".join(f"{lg}: {len(v)}" for lg, v in mds.items())}) in {DIST}')


if __name__ == '__main__':
    main()
