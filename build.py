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
DIST = os.environ.get('ODYRA_DIST') or os.path.join(ROOT, 'dist')  # ODYRA_DIST: cartella d'uscita alternativa
PAGINE = os.path.join(ROOT, 'pagine')

SITE = 'https://odyrasystemautomation.it'
EMAIL = 'team@odyrasystemautomation.it'
UPDATED = '2026-11-11'  # data dell'ultimo aggiornamento dei contenuti (sitemap, JSON-LD)
LINK_HAKO = 'https://hakocondomini.com'
# Pagina di prenotazione Google Calendar (Calendario → Programma di appuntamenti → Condividi → "Incorpora sul sito web":
# l'indirizzo che inizia con https://calendar.google.com/calendar/appointments/schedules/...). Vuoto = la pagina /prenota
# mostra il modulo contatti al posto del calendario.
BOOKING_URL = 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ1OY8thmgYsT5ahuiF3XfcvMsWsrHk-qNXZTg8Qc0pqzRI7kZIJuTzbqnSQo-OmBW2-HXcnT7_h'
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
# Ogni file .html in pagine/ (italiano, anche in sottocartelle) e in pagine/es/ (spagnolo) è una pagina.
# In cima al file c'è un commento con i dati della pagina:
#
#   <!--pagina
#   id: capabilities            (stesso id in italiano e spagnolo = la stessa pagina tradotta, per hreflang)
#   slug: capabilities          (indirizzo senza / iniziale e finale; vuoto per la home)
#   label: Agenti               (voce di menu e briciole di pane)
#   title: Agenti AI e servizi | Odyra
#   description: Il catalogo degli agenti ...
#   nav: 2                      (facoltativo: posizione nel menu in alto)
#   type: WebPage               (facoltativo: AboutPage, ContactPage, CollectionPage, FAQPage, Service...)
#   noindex: 1                  (facoltativo: pagina fuori da motori e sitemap)
#   parent: partner             (facoltativo: id della pagina madre, per le briciole di pane)
#   -->
#
# Le pagine "domande" e "privacy" sono generate qui sotto (GENERATED).
GENERATED = {
    'it': {
        'domande': dict(slug='domande', label='Domande frequenti', title='Domande frequenti su Odyra System e gli agenti AI',
                        description='Domande frequenti sugli agenti AI di Odyra System: come funzionano, canali, gestionali supportati, white-label, GDPR, AI Act e WhatsApp Business.', type='FAQPage'),
        'privacy': dict(slug='privacy', label='Privacy', title='Informativa privacy | Odyra System',
                        description='Informativa privacy di Odyra System (Verypos S.r.l.): quali dati raccogliamo dal modulo contatti e dalla demo vocale, cookie, finalità, conservazione e diritti.'),
    },
    'es': {
        'domande': dict(slug='preguntas', label='Preguntas frecuentes', title='Preguntas frecuentes sobre Odyra System y los agentes IA',
                        description='Preguntas frecuentes sobre los agentes IA de Odyra System: cómo funcionan, canales, software compatible, white-label, RGPD, AI Act y WhatsApp Business.', type='FAQPage'),
        'privacy': dict(slug='privacidad', label='Privacidad', title='Política de privacidad | Odyra System',
                        description='Política de privacidad de Odyra System (Verypos S.r.l.): qué datos recogemos del formulario y de la demo de voz, cookies, finalidades, conservación y derechos.'),
    },
}
NOINDEX_GENERATED = ()

META_RE = re.compile(r'\A\s*<!--pagina\s*\n(.*?)-->\s*', re.S)
REG = {lg: {} for lg in LANGS}   # lingua -> id -> dati della pagina (slug, label, title, description, src, ...)


def load_registry():
    for lang in LANGS:
        src_dir = PAGINE if lang == 'it' else os.path.join(PAGINE, 'es')
        found = {}
        for root, dirs, files in os.walk(src_dir):
            if lang == 'it' and os.path.abspath(root) == os.path.abspath(PAGINE) and 'es' in dirs:
                dirs.remove('es')
            dirs.sort()
            for fn in sorted(files):
                if not fn.endswith('.html'):
                    continue
                full = os.path.join(root, fn)
                with open(full, encoding='utf-8') as f:
                    text = f.read()
                m = META_RE.match(text)
                rel = os.path.relpath(full, ROOT)
                if not m:
                    raise SystemExit(f'{rel}: manca il commento <!--pagina ... --> in cima al file')
                meta = {}
                for line in m.group(1).splitlines():
                    if ':' in line:
                        k, v = line.split(':', 1)
                        meta[k.strip()] = re.sub(r'\s+\(.*\)\s*$', '', v.strip()) if k.strip() in ('nav', 'noindex') else v.strip()
                for need in ('id', 'label', 'title', 'description'):
                    if not meta.get(need):
                        raise SystemExit(f'{rel}: nel commento in cima manca "{need}"')
                meta.setdefault('slug', '')
                meta['slug'] = meta['slug'].strip('/')
                meta['src'] = full
                meta['body'] = text[m.end():]
                if meta['id'] in found:
                    raise SystemExit(f'{rel}: id "{meta["id"]}" già usato da {os.path.relpath(found[meta["id"]]["src"], ROOT)}')
                found[meta['id']] = meta
        for k, v in GENERATED[lang].items():
            found[k] = dict(v, id=k, src=None, body=None)
        slugs = {}
        for k, v in found.items():
            if v['slug'] in slugs:
                raise SystemExit(f'indirizzo "/{v["slug"]}" usato da due pagine: {k} e {slugs[v["slug"]]}')
            slugs[v['slug']] = k
        if 'home' not in found or 'contatti' not in found:
            raise SystemExit(f'pagine {lang}: servono almeno le pagine con id "home" e "contatti"')
        REG[lang] = dict(sorted(found.items(), key=lambda kv: (kv[1]['slug'] != '', kv[1]['slug'])))
        for k, v in REG[lang].items():
            TEXT[lang][k] = (v['slug'], v['label'], v['title'], v['description'])


def has(key, lang):
    return key in REG[lang]


def noindex(key, lang):
    v = REG[lang].get(key) or REG['it'].get(key) or {}
    return str(v.get('noindex', '0')) not in ('', '0', 'false', 'no')


def nav_items(lang):
    items = [(int(v['nav']), k) for k, v in REG[lang].items() if str(v.get('nav', '')).strip().isdigit()]
    return [k for _, k in sorted(items)]


# per lingua: id -> (indirizzo, etichetta, titolo, descrizione); riempito da load_registry()
TEXT = {lg: {} for lg in LANGS}

# testi fissi di testata, piede e pagine generate
UI = {
    'it': dict(skip='Vai al contenuto', menu='Menu', nav='Principale', demo='Prenota una call', other='ES', other_name='Español',
               about='Agenti AI vocali e WhatsApp dentro i gestionali verticali, in white-label per le software house. Milano, per l’Italia e la Spagna.',
               solutions='Soluzioni', resources='Risorse', sw='Software house', big='Grandi aziende', fr='Franchising e reti', ag='Agenzie e integratori',
               agents='Agenti e servizi', vat='Partita IVA', source='Fonte', updated='Aggiornato il',
               faq_lead='Modello partner, prezzi, canali, gestionali supportati, white-label, dati e AI Act: le risposte in breve.',
               faq_more='Non trovi la risposta? <a href="{c}">Scrivici</a>: rispondiamo entro un giorno lavorativo.',
               nf_title='Pagina non trovata', nf_lead='L’indirizzo non esiste o è stato spostato. Riparti dalla <a href="{h}">home</a> o <a href="{c}">scrivici</a>.',
               privacy_h1='Informativa sulla privacy.', privacy_lead='Come trattiamo i dati raccolti da questo sito.'),
    'es': dict(skip='Ir al contenido', menu='Menú', nav='Principal', demo='Reserva una llamada', other='IT', other_name='Italiano',
               about='Agentes IA de voz y WhatsApp dentro de los programas de gestión verticales, en white-label para empresas de software. Milán, para Italia y España.',
               solutions='Soluciones', resources='Recursos', sw='Empresas de software', big='Grandes empresas', fr='Franquicias y redes', ag='Agencias e integradores',
               agents='Agentes y servicios', vat='NIF-IVA', source='Fuente', updated='Actualizado el',
               faq_lead='Modelo de partners, precios, canales, software compatible, white-label, datos y AI Act: las respuestas en breve.',
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
    if key not in TEXT[lang]:
        lang = 'it'
    slug = TEXT[lang][key][0]
    return base(lang) + slug  # senza barra finale: gli indirizzi già indicizzati sono così


def md_path(key, lang):
    if key not in TEXT[lang]:
        lang = 'it'
    return base(lang) + (TEXT[lang][key][0] or 'index') + '.md'


# ───────── domande frequenti (pagina /domande/ e /es/preguntas/) ─────────
def faq_home():
    return [
        (t('Cos’è Odyra System?', '¿Qué es Odyra System?'),
         t('Odyra System, di Milano, è la piattaforma di agenti AI vocali e WhatsApp che lavorano dentro i gestionali verticali, in white-label per le software house. Gli agenti rispondono al telefono e su WhatsApp e prenotano, spostano e cancellano appuntamenti nel gestionale, seguendo le regole del settore. La software house li rivende ai propri centri col proprio marchio.',
           'Odyra System, de Milán, es la plataforma de agentes IA de voz y WhatsApp que trabajan dentro de los programas de gestión verticales, en white-label para las empresas de software. Los agentes contestan al teléfono y por WhatsApp y reservan, cambian y cancelan citas en el programa, siguiendo las reglas del sector. La empresa de software los revende a sus centros con su propia marca.')),
        (t('Che differenza c’è tra un agente di settore e un’AI generica?', '¿Qué diferencia hay entre un agente sectorial y una IA genérica?'),
         t('Un agente di settore ha le regole di quel mestiere scritte nel codice, non solo in un prompt: per un salone, per esempio, l’ordine colore-taglio-piega, i pacchetti e la regola delle 24 ore per le disdette. Inoltre legge e scrive direttamente nel software di gestione, quindi prenota solo orari realmente liberi.',
           'Un agente sectorial tiene las reglas de ese oficio escritas en el código, no solo en un prompt: en un salón, por ejemplo, el orden color-corte-peinado, los paquetes y la regla de 24 horas para cancelar. Además lee y escribe directamente en el software de gestión, así que solo reserva horarios realmente libres.')),
        (t('Su quali canali lavora l’agente?', '¿En qué canales trabaja el agente?'),
         t('Al telefono, con la voce in tempo reale, e su WhatsApp Business. È lo stesso agente su entrambi i canali, 24 ore su 24.',
           'Por teléfono, con voz en tiempo real, y por WhatsApp Business. Es el mismo agente en los dos canales, las 24 horas.')),
        (t('Dove è già in uso?', '¿Dónde se usa ya?'),
         t('Nel settore beauty: GoAgent è il servizio AI di BOSS per i saloni che usano il gestionale GoWeb, una rete di oltre 1.500 saloni in Italia. È in produzione da giugno 2026.',
           'En el sector de la belleza: GoAgent es el servicio IA de BOSS para los salones que usan el software GoWeb, una red de más de 1.500 salones en Italia. Está en producción desde junio de 2026.')),
    ]


def faq_partner():
    return [
        (t('Cosa serve a un gestionale per diventare partner?', '¿Qué necesita un software de gestión para ser partner?'),
         t('Dare accesso alle API per anagrafiche, agenda, turni e disponibilità. L’integrazione la scrive Odyra, a proprie spese, senza toccare il cuore del software.',
           'Dar acceso a las API de fichas de clientes, agenda, turnos y disponibilidad. La integración la escribe Odyra, a su cargo, sin tocar el núcleo del software.')),
        (t('Come guadagna il partner?', '¿Cómo gana el partner?'),
         t('Acquista da Odyra le licenze all’ingrosso, una per centro al mese, e le rivende ai propri centri col proprio marchio, al prezzo che decide. Per esempio la voce inbound S costa al partner 49 € al mese al primo scaglione, e il prezzo consigliato al centro è 79–89 €.',
           'Compra a Odyra las licencias al por mayor, una por centro al mes, y las revende a sus centros con su propia marca, al precio que decide. Por ejemplo, la voz entrante S le cuesta al partner 49 € al mes en el primer tramo, y el precio recomendado al centro es de 79–89 €.')),
        (t('Quanto costa partire?', '¿Cuánto cuesta empezar?'),
         t('Integrazione e dashboard white-label sono a carico di Odyra e la beta è gratuita fino a 5 centri per 60 giorni. Al termine della beta l’impegno minimo è di 20 licenze per 12 mesi, fatturate mensilmente.',
           'La integración y el panel white-label corren a cargo de Odyra y la beta es gratuita para hasta 5 centros durante 60 días. Al terminar la beta, el compromiso mínimo es de 20 licencias durante 12 meses, facturadas mensualmente.')),
        (t('Con quale marchio arriva ai centri?', '¿Con qué marca llega a los centros?'),
         t('Con quello del partner: nome dell’agente, messaggi e dashboard nello stile grafico del gestionale.', 'Con la del partner: nombre del agente, mensajes y panel con el estilo gráfico del programa.')),
        (t('Chi segue i centri dopo l’attivazione?', '¿Quién atiende a los centros después de la activación?'),
         t('Odyra: attivazione di numero e canale WhatsApp, qualità delle conversazioni, consumi e assistenza tecnica sull’agente. Il partner resta il riferimento commerciale.',
           'Odyra: activación del número y del canal WhatsApp, calidad de las conversaciones, consumos y soporte técnico del agente. El partner sigue siendo la referencia comercial.')),
    ]


def faq_all():
    return faq_home() + faq_partner() + [
        (t('Con quali software di gestione funziona?', '¿Con qué software de gestión funciona?'),
         t('Con ogni software di gestione che espone le API per clienti, disponibilità e appuntamenti: per ciascuno Odyra scrive un connettore dedicato. Oggi è in produzione nel beauty con GoWeb di BOSS; dentale, poliambulatori e gli altri servizi su appuntamento sono i verticali successivi.',
           'Con cualquier software de gestión que exponga API de clientes, disponibilidad y citas: para cada uno Odyra escribe un conector dedicado. Hoy está en producción en el sector de la belleza con GoWeb de BOSS; clínicas dentales, policlínicas y los demás servicios con cita previa son los siguientes sectores.')),
        (t('Quanto costa?', '¿Cuánto cuesta?'),
         t('Si paga una licenza per centro al mese: voce, WhatsApp o combo, in taglia S, M o L. Per le software house il prezzo è all’ingrosso, da 22 € a licenza, con scaglioni di volume; il prezzo al centro lo decide il partner. Le aziende acquistano direttamente gli stessi pacchetti, da 39 € per sede al mese. I costi WhatsApp sono inclusi nei pacchetti WhatsApp e Combo. Prezzi IVA esclusa.',
           'Se paga una licencia por centro al mes: voz, WhatsApp o combo, en talla S, M o L. Para las empresas de software el precio es mayorista, desde 22 € por licencia, con tramos de volumen; el precio al centro lo decide el partner. Las empresas compran directamente los mismos paquetes, desde 39 € por sede al mes. Los costes de WhatsApp están incluidos en los paquetes WhatsApp y Combo. Precios sin IVA.')),
        (t('Quanto ci vuole per attivare un nuovo cliente?', '¿Cuánto se tarda en activar un cliente nuevo?'),
         t('Con il software di gestione già collegato, staff e listino si sincronizzano da soli e uno specialista Odyra attiva numero, WhatsApp e voce in circa dieci minuti.',
           'Con el software de gestión ya conectado, equipo y tarifas se sincronizan solos y un especialista de Odyra activa número, WhatsApp y voz en unos diez minutos.')),
        (t('L’agente dice di essere un’intelligenza artificiale?', '¿El agente dice que es una inteligencia artificial?'),
         t('Sì, sempre, sia al telefono sia su WhatsApp, come richiede l’AI Act europeo.', 'Sí, siempre, tanto por teléfono como por WhatsApp, como exige el AI Act europeo.')),
        (t('Cosa succede se l’agente non sa rispondere?', '¿Qué pasa si el agente no sabe responder?'),
         t('Passa la conversazione a una persona, anche durante una chiamata. Su WhatsApp il titolare può prendere in carico la conversazione e restituirla all’AI quando vuole.',
           'Pasa la conversación a una persona, incluso durante una llamada. En WhatsApp el titular puede tomar la conversación y devolvérsela a la IA cuando quiera.')),
        (t('Come vengono trattati i dati?', '¿Cómo se tratan los datos?'),
         t('Ogni azienda ha un agente con dati e configurazione isolati. Il trattamento è conforme al GDPR e progettato nel rispetto dell’AI Act.',
           'Cada empresa tiene un agente con datos y configuración aislados. El tratamiento cumple el RGPD y está diseñado respetando el AI Act.')),
        (t('Di chi è il numero WhatsApp Business?', '¿De quién es el número de WhatsApp Business?'),
         t('Del cliente. Odyra attiva il numero sul canale ufficiale WhatsApp Business e gestisce template e conversazioni, ma la titolarità dell’account resta al cliente.',
           'Del cliente. Odyra activa el número en el canal oficial de WhatsApp Business y gestiona plantillas y conversaciones, pero la titularidad de la cuenta sigue siendo del cliente.')),
        (t('Cos’è HAKO?', '¿Qué es HAKO?'),
         t('HAKO è un software proprietario di Odyra per le portinerie dei condomini, venduto direttamente. Ha un sito dedicato: hakocondomini.com.',
           'HAKO es un software propio de Odyra para las conserjerías de comunidades de vecinos, vendido directamente. Tiene una web propia: hakocondomini.com.')),
        (t('Odyra lavora anche con aziende che non sono software house?', '¿Odyra trabaja también con empresas que no son de software?'),
         t('Sì. Gruppi multi-sede, catene e aziende con molte chiamate acquistano direttamente gli stessi pacchetti dei partner, con un prezzo per sede che scende all’aumentare delle sedi. Per le aziende con grandi volumi ci sono anche progetti su misura: agenti commerciali che richiamano i lead in pochi secondi, customer service e automazioni di back office, integrati con CRM ed ERP.',
           'Sí. Los grupos multisede, las cadenas y las empresas con muchas llamadas compran directamente los mismos paquetes que los partners, con un precio por sede que baja a medida que crecen las sedes. Para empresas con grandes volúmenes hay también proyectos a medida: agentes comerciales que llaman a los leads en segundos, atención al cliente y automatizaciones de back office, integrados con CRM y ERP.')),
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
        'description': t('Piattaforma di agenti AI vocali e WhatsApp che lavorano dentro i gestionali verticali, in white-label per le software house, con licenze all’ingrosso per centro. Milano.',
                         'Plataforma de agentes IA de voz y WhatsApp que trabajan dentro de los programas de gestión verticales, en white-label para las empresas de software, con licencias mayoristas por centro. Milán.'),
        'slogan': t('Voi mettete il marchio. Noi il motore.', 'Vosotros ponéis la marca. Nosotros, el motor.'),
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
    """Informativa privacy (it/es), coerente con ciò che il sito fa davvero: modulo contatti, demo vocale,
    cookie tecnici, statistica e marketing solo con consenso. Testo da far rivedere a un legale."""
    u = UI[lang]
    mail = f'<a href="mailto:{EMAIL}">{EMAIL}</a>'
    cookie = path('cookie', 'it') if has('cookie', lang) or has('cookie', 'it') else '#'
    city = t('Milano', 'Milán')
    prefs = t('<button type="button" class="b b-line" data-cookie-prefs>Preferenze cookie</button>',
              '<button type="button" class="b b-line" data-cookie-prefs>Preferencias de cookies</button>')
    sections = [
        (t('Titolare del trattamento', 'Responsable del tratamiento'), [
            t(f'{COMPANY["legal"]}, {COMPANY["street"]}, {COMPANY["zip"]} {city}, {u["vat"]} {COMPANY["vat"]} (di seguito «Odyra»). Per ogni domanda sui tuoi dati scrivi a {mail}.',
              f'{COMPANY["legal"]}, {COMPANY["street"]}, {COMPANY["zip"]} {city} (Italia), {u["vat"]} {COMPANY["vat"]} (en adelante, «Odyra»). Para cualquier pregunta sobre tus datos escribe a {mail}.')]),
        (t('Modulo contatti', 'Formulario de contacto'), [
            t('Quando ci scrivi dal modulo raccogliamo nome, e-mail, azienda, telefono, l’esigenza e il messaggio che inserisci, la pagina da cui scrivi e, se arrivi da un annuncio, i parametri della campagna (per esempio la sorgente e l’identificativo del clic). Ti mandiamo un’e-mail di conferma all’indirizzo che hai indicato.',
              'Cuando nos escribes desde el formulario recogemos nombre, correo, empresa, teléfono, la necesidad y el mensaje que introduces, la página desde la que escribes y, si llegas desde un anuncio, los parámetros de la campaña (por ejemplo, la fuente y el identificador del clic). Te enviamos un correo de confirmación a la dirección indicada.'),
            t('Finalità: rispondere alla richiesta e, se lo chiedi, preparare una proposta. Base giuridica: misure precontrattuali su tua richiesta e legittimo interesse a capire quali canali ci portano i contatti (art. 6.1 b e f GDPR). Conserviamo i dati per il tempo necessario a gestire la richiesta e comunque non oltre 24 mesi dall’ultimo contatto, salvo che ne nasca un rapporto contrattuale.',
              'Finalidad: responder a la solicitud y, si lo pides, preparar una propuesta. Base jurídica: medidas precontractuales a petición tuya e interés legítimo en saber qué canales nos traen los contactos (art. 6.1 b y f RGPD). Conservamos los datos el tiempo necesario para gestionar la solicitud y en todo caso no más de 24 meses desde el último contacto, salvo que surja una relación contractual.')]),
        (t('Demo vocale', 'Demo de voz'), [
            t('La demo vocale è facoltativa: parte solo quando premi il pulsante e autorizzi il microfono, e termina quando chiudi il pannello. Parli con un’intelligenza artificiale, non con una persona. L’audio del microfono è elaborato in tempo reale per capire cosa dici e generare la risposta. Non usiamo la conversazione per identificarti né per profilarti; ti chiediamo di non comunicare dati personali o informazioni sensibili durante la demo.',
              'La demo de voz es opcional: empieza solo cuando pulsas el botón y autorizas el micrófono, y termina cuando cierras el panel. Hablas con una inteligencia artificial, no con una persona. El audio del micrófono se procesa en tiempo real para entender lo que dices y generar la respuesta. No usamos la conversación para identificarte ni para perfilarte; te pedimos que no comuniques datos personales ni información sensible durante la demo.'),
            t('Per collegarti, il servizio tratta dati tecnici (indirizzo IP, orario e durata della sessione, lingua della pagina), conservati per il tempo necessario a garantire sicurezza e funzionamento. Base giuridica: la tua richiesta di provare il servizio e il nostro legittimo interesse alla sicurezza (art. 6.1 b e f GDPR).',
              'Para conectarte, el servicio trata datos técnicos (dirección IP, hora y duración de la sesión, idioma de la página), conservados el tiempo necesario para garantizar seguridad y funcionamiento. Base jurídica: tu solicitud de probar el servicio y nuestro interés legítimo en la seguridad (art. 6.1 b y f RGPD).')]),
        (t('Navigazione, cookie e misurazione', 'Navegación, cookies y medición'), [
            t('Il server registra dati tecnici di navigazione (indirizzo IP, pagina richiesta, browser) per sicurezza e per prevenire abusi, con conservazione breve. Caratteri e librerie del sito sono ospitati sul nostro server.',
              'El servidor registra datos técnicos de navegación (dirección IP, página solicitada, navegador) por seguridad y para prevenir abusos, con conservación breve. Las fuentes y librerías del sitio están alojadas en nuestro servidor.'),
            t(f'Usiamo cookie tecnici e, solo con il tuo consenso, cookie di statistica e di marketing. Senza consenso, il tag pubblicitario invia solo segnali senza cookie e senza identificatori, utili a una misura aggregata. Il dettaglio dei cookie e dei servizi usati è nella <a href="{cookie}">cookie policy</a>; puoi cambiare scelta in ogni momento.',
              f'Usamos cookies técnicas y, solo con tu consentimiento, cookies de estadística y de marketing. Sin consentimiento, la etiqueta publicitaria solo envía señales sin cookies y sin identificadores, útiles para una medición agregada. El detalle de las cookies y servicios usados está en la <a href="{cookie}">política de cookies</a> (en italiano); puedes cambiar tu elección en cualquier momento.'),
            prefs]),
        (t('A chi comunichiamo i dati', 'A quién comunicamos los datos'), [
            t('I dati sono trattati dal personale autorizzato di Odyra e da fornitori che ci aiutano a gestire il sito: ospitalità e infrastruttura, invio delle e-mail, infrastruttura della demo vocale, misurazione e pubblicità (solo con consenso). Agiscono come responsabili del trattamento con un accordo scritto. Non vendiamo i dati a nessuno.',
              'Los datos los trata el personal autorizado de Odyra y proveedores que nos ayudan a gestionar el sitio: alojamiento e infraestructura, envío de correos, infraestructura de la demo de voz, medición y publicidad (solo con consentimiento). Actúan como encargados del tratamiento con un acuerdo por escrito. No vendemos los datos a nadie.'),
            t('Alcuni fornitori possono trattare dati fuori dallo Spazio economico europeo: in quel caso il trasferimento avviene sulla base di una decisione di adeguatezza della Commissione europea o delle clausole contrattuali standard.',
              'Algunos proveedores pueden tratar datos fuera del Espacio Económico Europeo: en ese caso la transferencia se basa en una decisión de adecuación de la Comisión Europea o en las cláusulas contractuales tipo.')]),
        (t('I tuoi diritti', 'Tus derechos'), [
            t(f'Puoi chiedere l’accesso ai tuoi dati, la rettifica, la cancellazione, la limitazione, la portabilità e opporti al trattamento basato sul legittimo interesse (artt. 15-22 GDPR), scrivendo a {mail}. Puoi revocare il consenso ai cookie in ogni momento. Hai diritto di presentare reclamo al Garante per la protezione dei dati personali (garanteprivacy.it).',
              f'Puedes pedir el acceso a tus datos, su rectificación, supresión, limitación y portabilidad, y oponerte al tratamiento basado en el interés legítimo (arts. 15-22 RGPD), escribiendo a {mail}. Puedes retirar el consentimiento a las cookies en cualquier momento. Tienes derecho a presentar una reclamación ante la autoridad de control: en Italia el Garante per la protezione dei dati personali, en España la Agencia Española de Protección de Datos (aepd.es).')]),
        (t('Aggiornamenti', 'Actualizaciones'), [
            t(f'Possiamo aggiornare questa informativa quando cambia il sito o la normativa. Ultimo aggiornamento: {UPDATED}.',
              f'Podemos actualizar esta política cuando cambien el sitio o la normativa. Última actualización: {UPDATED}.')]),
    ]
    inner = ''.join(f'\n    <h2>{h}</h2>' + ''.join(f'\n    {p}' if p.startswith('<button') else f'\n    <p>{p}</p>' for p in ps) for h, ps in sections)
    return phead(lang, TEXT[lang]['privacy'][1], u['privacy_h1'], u['privacy_lead']) + f'''
<section class="band paper">
  <div class="wrap prose">{inner}
  </div>
</section>'''


def booking_block(lang):
    """Calendario per prenotare una call, incorporato nella pagina /prenota; senza indirizzo, rimanda al modulo."""
    if BOOKING_URL:
        if not BOOKING_URL.startswith('https://calendar.google.com/'):
            raise SystemExit('BOOKING_URL deve iniziare con https://calendar.google.com/ (indirizzo "Incorpora" della pagina di prenotazione)')
        src = BOOKING_URL + ('&' if '?' in BOOKING_URL else '?') + 'gv=true'
        return (f'<div class="booking-frame"><iframe src="{e(src)}" title="{t("Calendario per prenotare una call con Odyra", "Calendario para reservar una llamada con Odyra")}" '
                f'loading="lazy" width="100%" height="720"></iframe></div>'
                f'<p class="sec-lead booking-alt">{t("Il calendario non si carica?", "¿El calendario no carga?")} '
                f'<a href="{e(BOOKING_URL)}" target="_blank" rel="noopener">{t("Apri la pagina di prenotazione", "Abre la página de reservas")}</a>.</p>')
    return (f'<div class="booking-frame booking-empty"><p>{t("Scrivici quando preferisci: ti proponiamo noi due orari entro un giorno lavorativo.", "Escríbenos cuándo prefieres: te proponemos dos horarios en un día laborable.")}</p>'
            f'<p class="actions"><a class="b b-cyan" href="{path("contatti", lang)}?interesse=demo">{t("Scegli un orario", "Elige un horario")}</a> '
            f'<a class="b b-line" href="mailto:{EMAIL}?subject={t("Prenotazione%20call", "Reserva%20llamada")}">{EMAIL}</a></p></div>')


def url_or_warn(key, lang, src):
    if has(key, lang) or has(key, 'it'):
        return path(key, lang)
    print(f'Attenzione: {os.path.relpath(src, ROOT)} rimanda a {{{{URL:{key}}}}}, pagina che non esiste (per ora punta a #)')
    return '#'


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
    for key, meta in REG[lang].items():
        if meta['src']:
            body = meta['body']
            body = body.replace('{{AGENTS_N}}', str(len(cards))).replace('{{AGENTS}}', ''.join(cards)).replace('{{AGENTS_GRID}}', grid).replace('{{P}}', base(lang))
            body = re.sub(r'\{\{URL:([a-z0-9-]+)\}\}', lambda m: url_or_warn(m.group(1), lang, meta['src']), body)
            if '{{BOOKING}}' in body:
                body = body.replace('{{BOOKING}}', booking_block(lang))
            body = without_placeholders(body)
            if re.search(r'slot-mini|slot-box|partner-slot', body):
                print(f'Attenzione: in {os.path.relpath(meta["src"], ROOT)} è rimasto un segnaposto da riempire')
        else:
            body = body_domande(lang) if key == 'domande' else body_privacy(lang)
        out[key] = body.replace('<p class="crumbs">', '<p class="crumbs" data-md="skip">').strip()
    return out


# ───────── testata, piede, <head> ─────────
def header(lang, current):
    u = UI[lang]
    links = ''.join(f'<li><a href="{path(k, lang)}"{" aria-current=\"page\"" if k == current else ""}>{TEXT[lang][k][1]}</a></li>' for k in nav_items(lang))
    other = 'es' if lang == 'it' else 'it'
    switch = path(current, other) if current and has(current, other) else base(other)
    close = 'Chiudi' if lang == 'it' else 'Cerrar'
    return f'''<header class="top">
  <a class="top-brand" href="{base(lang)}"><img src="/assets/logos/odyra-system.webp" alt="Odyra System" width="150" height="40"></a>
  <nav class="top-nav" id="nav" aria-label="{u['nav']}">
    <ul class="top-links">{links}</ul>
    <div class="top-side">
      <a class="top-lang" href="{switch}" hreflang="{other}" lang="{other}"><span aria-hidden="true">{u['other']}</span><span class="sr">{u['other_name']}</span></a>
      <a class="b b-cyan top-cta" href="{path('prenota' if has('prenota', lang) or has('prenota', 'it') else 'contatti', lang)}">{t('Prenota una call', 'Reserva una llamada')}</a>
    </div>
  </nav>
  <button class="top-menu" id="menu" type="button" aria-expanded="false" aria-controls="nav" data-open="{u['menu']}" data-close="{close}"><span class="top-menu-icon" aria-hidden="true"><i></i><i></i></span><span class="top-menu-label">{u['menu']}</span></button>
</header>'''


# Colonne del piede: (titolo it, titolo es, [id di pagina o (etichetta, indirizzo)]). Le pagine mancanti in una lingua si saltano.
# Le pagine legali (privacy, cookie, termini) stanno nella riga in fondo, accanto alle preferenze cookie.
FOOTER = [
    ('Soluzioni', 'Soluciones', ['soluzioni', 'centralino-ai', 'segretaria-ai', 'settore-estetica', 'settore-dentale', 'partner']),
    ('Odyra', 'Odyra', ['capabilities', 'tecnologie', 'processo', 'lavori', 'eventi', 'studio', 'team']),
    ('Risorse', 'Recursos', ['demo', 'contatti', 'domande']),
]
FOOTER_LEGAL = ['privacy', 'cookie', 'termini']


def footer(lang):
    u = UI[lang]
    other = 'es' if lang == 'it' else 'it'

    def items(ids):
        out = []
        for k in ids:
            if isinstance(k, tuple):
                out.append(k)
            elif has(k, lang):
                out.append((TEXT[lang][k][1], path(k, lang)))
        return out
    col = lambda title, its: (f'<div class="foot-col"><h2>{title}</h2><ul>' + ''.join(f'<li><a href="{h}">{l}</a></li>' for l, h in its) + '</ul></div>') if its else ''
    cols = ''.join(col(ti if lang == 'it' else te, items(ids)) for ti, te, ids in FOOTER)
    legal = ''.join(f'<li><a href="{h}">{l}</a></li>' for l, h in items(FOOTER_LEGAL))
    prefs = 'Preferenze cookie' if lang == 'it' else 'Preferencias de cookies'
    claim = 'Un solo cervello, mille sedi, il vostro nome sopra.' if lang == 'it' else 'Un solo cerebro, mil sedes, vuestro nombre encima.'
    city = 'Milano' if lang == 'it' else 'Milán'
    return f'''<footer class="foot ink">
  <div class="wrap">
    <p class="foot-claim">{claim}</p>
    <div class="foot-cols">
      <div class="foot-about">
        <img src="/assets/logos/odyra-system.webp" alt="Odyra System" width="150" height="40" loading="lazy">
        <p>{u['about']}</p>
        <p class="foot-contact"><a href="mailto:{EMAIL}">{EMAIL}</a><br>{COMPANY['street']}, {COMPANY['zip']} {city}</p>
      </div>
      {cols}
    </div>
    <div class="foot-base">
      <p class="foot-legal">© 2026 Odyra System, {COMPANY['legal']}, {u['vat']} {COMPANY['vat']}, REA {COMPANY['rea']}.</p>
      <ul class="foot-meta">{legal}<li><button type="button" class="foot-link" data-cookie-prefs>{prefs}</button></li><li><a href="{base(other)}" hreflang="{other}" lang="{other}">{u['other_name']}</a></li></ul>
    </div>
  </div>
</footer>'''


def qa_pairs(body):
    """Domande e risposte di una pagina (<details><summary>), per il JSON-LD FAQPage."""
    return [(strip(q), strip(a)) for q, a in re.findall(r'<details><summary>(.*?)</summary>(.*?)</details>', body, re.S)]


def jsonld(lang, key, body):
    _, label, title, desc = TEXT[lang][key]
    meta = REG[lang][key]
    page_url = SITE + path(key, lang)
    ptype = meta.get('type') or {'domande': 'FAQPage'}.get(key, 'WebPage')
    page = {'@type': ptype if ptype != 'Service' else 'WebPage',
            '@id': page_url + '#page', 'url': page_url, 'name': title, 'description': desc,
            'inLanguage': 'it-IT' if lang == 'it' else 'es-ES',
            'isPartOf': {'@id': f'{SITE}/#website'}, 'about': {'@id': f'{SITE}/#org'},
            'dateModified': UPDATED, 'primaryImageOfPage': og_image(lang)}
    if key != 'home':
        trail = [(TEXT[lang]['home'][1], SITE + base(lang))]
        parent = meta.get('parent')
        if parent and has(parent, lang):
            trail.append((TEXT[lang][parent][1], SITE + path(parent, lang)))
        trail.append((label, page_url))
        # nomi uguali alle briciole visibili nella pagina, se ci sono e hanno gli stessi livelli
        m = re.search(r'<p class="crumbs"[^>]*>(.*?)</p>', body, re.S)
        shown = [strip(x).strip() for x in m.group(1).split('<span aria-hidden="true">/</span>')] if m else []
        if len(shown) == len(trail) and all(shown):
            trail = [(n, it) for n, (_, it) in zip(shown, trail)]
        page['breadcrumb'] = {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': it} for i, (n, it) in enumerate(trail)]}
    nodes = [org_node(),
             {'@type': 'WebSite', '@id': f'{SITE}/#website', 'url': f'{SITE}/', 'name': 'Odyra System', 'inLanguage': ['it-IT', 'es-ES'], 'publisher': {'@id': f'{SITE}/#org'}},
             page]
    qa = qa_pairs(body)
    if qa:
        main = [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in qa]
        if ptype == 'FAQPage':
            page['mainEntity'] = main
        else:
            nodes.append({'@type': 'FAQPage', '@id': page_url + '#faq', 'url': page_url, 'mainEntity': main})
    if ptype == 'Service':
        nodes.append({'@type': 'Service', '@id': page_url + '#service', 'name': re.sub(r'\s*\|[^|]*$', '', title), 'description': desc, 'url': page_url,
                      'provider': {'@id': f'{SITE}/#org'}, 'areaServed': ['IT', 'ES'], 'serviceType': label})
    return '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': nodes}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + '</script>'


def voice_nav(lang):
    """Pagine verso cui l'agente della demo vocale può portare il visitatore (vedi static/odyra-app.js)."""
    pick = lambda *ids: next((path(k, lang) for k in ids if has(k, lang) or has(k, 'it')), base(lang))
    return json.dumps({'home': base(lang), 'contatti': pick('contatti'), 'case': pick('case-boss', 'lavori'), 'lavori': pick('lavori')},
                      separators=(',', ':'))


def layout(lang, key, body, title=None, desc=None, not_found=False):
    _, _, page_title, page_desc = TEXT[lang][key]
    title, desc = title or page_title, desc or page_desc
    u = UI[lang]
    if not_found:
        seo = '<meta name="robots" content="noindex,follow">'
    else:
        url = SITE + path(key, lang)
        noindex = globals()['noindex'](key, lang)
        langs = [lg for lg in LANGS if has(key, lg)]
        alts = (''.join(f'<link rel="alternate" hreflang="{lg}" href="{SITE}{path(key, lg)}">' for lg in langs) + f'<link rel="alternate" hreflang="x-default" href="{SITE}{path(key, "it")}">') if len(langs) > 1 else ''
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
<script src="/odyra-app.js?v={ASSET_V}" data-v="{ASSET_V}" data-voice-nav="{e(voice_nav(lang))}"></script>
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{seo}
<meta name="theme-color" content="#071A3A">
<link rel="icon" href="/assets/icons/favicon.ico" sizes="any"><link rel="icon" href="/assets/icons/fav-48.png" type="image/png" sizes="48x48"><link rel="apple-touch-icon" href="/assets/icons/fav-180.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="preload" href="/assets/fonts/archivo-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/odyra.css?v={ASSET_V}">
<link rel="stylesheet" href="/odyra-app.css?v={ASSET_V}">
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
    # mds: lingua -> id -> markdown, solo pagine indicizzabili
    if full:
        head = ('# Odyra System: testo completo del sito / texto completo del sitio\n\n'
                f'> Tutte le pagine pubbliche di {SITE} in Markdown, in italiano e in spagnolo. Aggiornato il {UPDATED}.\n\n')
        return head + '\n\n---\n\n'.join(mds[lg][k] for lg in LANGS for k in mds[lg])
    out = ['# Odyra System', '',
           '> Odyra System (Milano, Verypos S.r.l.) è la piattaforma di agenti AI vocali e WhatsApp che lavorano dentro i gestionali verticali, in white-label per le software house. Si parte dai saloni con BOSS.', '',
           'Fatti chiave:', '',
           '- Agenti per voce (telefono in tempo reale, in entrata e in uscita) e WhatsApp Business: riconoscono il cliente, prenotano, spostano e cancellano appuntamenti nel gestionale, seguono le regole del centro e passano all’operatore quando serve.',
           '- In produzione nel settore beauty con GoAgent, il servizio AI di BOSS per gli oltre 1.500 saloni che usano il gestionale GoWeb, da giugno 2026. Dentale, poliambulatori e altri servizi su appuntamento sono i verticali successivi.',
           '- Modello wholesale per le software house: licenza per centro al mese (voce, WhatsApp o combo, taglie S, M, L), da 22 € all’ingrosso con scaglioni di volume su tutte le licenze; il partner rivende col proprio marchio e decide il prezzo al centro. Integrazione con le API del gestionale e dashboard white-label incluse, a carico di Odyra. Beta gratuita fino a 5 centri per 60 giorni. Costi WhatsApp inclusi nei pacchetti WhatsApp e Combo. Prezzi IVA esclusa.',
           '- Secondo pubblico: gruppi multi-sede e aziende con molte chiamate, che acquistano gli stessi pacchetti direttamente, da 39 € per sede al mese; progetti su misura per le grandi aziende.',
           '- L’agente dice sempre di essere un’AI (AI Act); dati isolati per cliente, conforme al GDPR.',
           '- Altri prodotti e servizi: HAKO, software proprietario per le portinerie dei condomini (https://hakocondomini.com); progetti su misura (es. Gruppo Colzani); Odyra Academy, consulenza e formazione sull’AI.',
           f'- Contatti: {EMAIL}, {COMPANY["street"]}, {COMPANY["zip"]} {COMPANY["city"]}, Italia.', '',
           'Ogni pagina ha una versione Markdown allo stesso indirizzo con estensione .md. Il testo completo è in /llms-full.txt.', '']
    for lg, title in (('it', '## Pagine (italiano)'), ('es', '## Páginas (español)')):
        out += [title, '']
        out += [f'- [{TEXT[lg][k][1]}]({SITE}{md_path(k, lg)}): {TEXT[lg][k][3]}' for k in mds[lg]]
        out.append('')
    out += ['## Optional', '', f'- [Testo completo / Texto completo]({SITE}/llms-full.txt): tutte le pagine in un unico file.',
            f'- [Sitemap]({SITE}/sitemap.xml)', '']
    return '\n'.join(out)


def sitemap():
    rows = []
    for lg in LANGS:
        for k in REG[lg]:
            if noindex(k, lg):
                continue
            langs = [x for x in LANGS if has(k, x) and not noindex(k, x)]
            alts = ''
            if len(langs) > 1:
                alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{SITE}{path(k, x)}"/>' for x in langs)
                alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{path(k, "it")}"/>'
            depth = TEXT[lg][k][0].count('/') + (1 if TEXT[lg][k][0] else 0)
            prio = '1.0' if k == 'home' else ('0.9' if depth == 1 else '0.8')
            rows.append(f'<url><loc>{SITE}{path(k, lg)}</loc><lastmod>{UPDATED}</lastmod><priority>{prio}</priority>{alts}</url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + '\n'.join(rows) + '\n</urlset>\n')


ROBOTS = f'''# Odyra System. Tutti i contenuti pubblici sono aperti ai motori di ricerca e agli assistenti AI.
# Versione per modelli linguistici: {SITE}/llms.txt (testo completo: {SITE}/llms-full.txt)

User-agent: *
Allow: /
Disallow: /api/

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
Disallow: /api/

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
    shutil.copytree(STATIC, DIST, ignore=shutil.ignore_patterns('.*'))  # niente file nascosti (.gitkeep) nel sito
    ASSET_V = asset_version('odyra.css', 'odyra.js', 'odyra-app.css', 'odyra-app.js', 'assets/vendor/rtc-client.min.js')
    load_registry()
    mds = {}
    for lang in LANGS:
        L = lang
        mds[lang] = {}
        for key, body in bodies(lang).items():
            slug = TEXT[lang][key][0]
            write(f'{base(lang)}{slug + "/" if slug else ""}index.html', layout(lang, key, body))
            if not noindex(key, lang):
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
