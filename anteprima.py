#!/usr/bin/env python3
"""Genera l'anteprima del nuovo sito in static/anteprima/ (solo italiano, noindex).

Le pagine stanno in anteprima-src/*.html (solo il contenuto di <main>); testata, piede e <head> li aggiunge questo script.
Segnaposti nei sorgenti: {{P}} = percorso relativo alla radice dell'anteprima, {{AGENTS}} = card del catalogo,
{{AGENTS_GRID}} = catalogo completo diviso per categoria.
Uso: python3 anteprima.py   (poi python3 build.py copia tutto in dist/)
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'anteprima-src')
OUT = os.path.join(ROOT, 'static', 'anteprima')
V = '6'

# slug, file sorgente, titolo, descrizione, voce di menu
PAGES = [
    ('', 'home.html', 'Odyra System: agenti AI col tuo marchio', 'La fabbrica di agenti AI white-label.', None),
    ('soluzioni', 'soluzioni.html', 'Soluzioni per software house, aziende, reti e agenzie | Odyra', 'Come Odyra lavora con software house, grandi aziende, franchising e agenzie.', 'Soluzioni'),
    ('agenti', 'agenti.html', 'Agenti e servizi | Odyra', 'Il catalogo degli agenti AI e dei servizi Odyra.', 'Agenti'),
    ('piattaforma', 'piattaforma.html', 'La piattaforma | Odyra', 'Come è fatta la piattaforma Odyra.', 'Piattaforma'),
    ('academy', 'academy.html', 'Odyra Academy: consulenza e formazione sull’AI | Odyra', 'Workshop, webinar, percorsi e consulenza sull’intelligenza artificiale per le aziende.', 'Academy'),
    ('casi', 'casi.html', 'Casi di successo | Odyra', 'BOSS e Gruppo Colzani: agenti Odyra al lavoro.', 'Casi di successo'),
    ('chi-siamo', 'chi-siamo.html', 'Chi siamo | Odyra', 'Odyra System, gruppo tecnologico di Milano.', 'Chi siamo'),
    ('contatti', 'contatti.html', 'Contatti | Odyra', 'Richiedi una demo o un workshop.', None),
]

CATS = [('voce', 'Voce', 'Agenti che parlano al telefono, in entrata e in uscita, e dal vostro sito.'),
        ('messaggi', 'Messaggi', 'WhatsApp, promemoria, recensioni, in più lingue.'),
        ('vendite', 'Vendite', 'Lead, ordini, solleciti: gli agenti che portano e difendono il fatturato.'),
        ('assistenza', 'Assistenza', 'Clienti e dipendenti con una risposta giusta, a qualsiasi ora.'),
        ('operazioni', 'Operazioni', 'Il lavoro ripetitivo dietro le quinte: documenti, dati, flussi.'),
        ('qualita', 'Qualità e dati', 'Gli agenti che controllano gli altri agenti, e i report per chi decide.'),
        ('infrastruttura', 'Infrastruttura', 'Dove gira l’AI e come si collega ai vostri sistemi.')]


def page_path(slug):
    return os.path.join(OUT, slug, 'index.html') if slug else os.path.join(OUT, 'index.html')


def header(p, current):
    links = ''.join(f'<a href="{p}{s}/"{" aria-current=\"page\"" if s == current else ""}>{label}</a>' for s, _, _, _, label in PAGES if label)
    return f'''<header class="top">
  <a class="top-brand" href="{p or './'}"><img src="/assets/logos/odyra-system.webp" alt="Odyra System" width="150" height="40"></a>
  <nav class="top-nav" id="nav" aria-label="Principale">
    {links}
    <a class="b b-cyan" href="{p}contatti/">Richiedi una demo</a>
  </nav>
  <button class="top-menu" id="menu" type="button" aria-expanded="false" aria-controls="nav">Menu</button>
</header>'''


def footer(p):
    col = lambda t, items: f'<div><h2>{t}</h2><ul>' + ''.join(f'<li><a href="{h}">{l}</a></li>' for l, h in items) + '</ul></div>'
    return f'''<footer class="foot ink">
  <div class="wrap">
    <div class="foot-cols">
      <div class="foot-about"><img src="/assets/logos/odyra-system.webp" alt="Odyra System" width="150" height="40" loading="lazy"><p>La fabbrica di agenti AI white-label. Milano, per l’Italia e la Spagna.</p></div>
      {col('Soluzioni', [('Software house', p + 'soluzioni/#software-house'), ('Grandi aziende', p + 'soluzioni/#grandi-aziende'), ('Franchising e reti', p + 'soluzioni/#franchising'), ('Agenzie e integratori', p + 'soluzioni/#agenzie')])}
      {col('Odyra', [('Agenti e servizi', p + 'agenti/'), ('Piattaforma', p + 'piattaforma/'), ('Odyra Academy', p + 'academy/'), ('Casi di successo', p + 'casi/'), ('Chi siamo', p + 'chi-siamo/')])}
      {col('Contatti', [('Richiedi una demo', p + 'contatti/'), ('team@odyrasystemautomation.it', 'mailto:team@odyrasystemautomation.it'), ('Privacy', '/privacy/')])}
    </div>
    <p class="foot-legal">Odyra System, Verypos S.r.l. Viale Papiniano 8, 20123 Milano. Partita IVA 11630390968, REA MI-2615892.</p>
  </div>
</footer>'''


def layout(slug, title, desc, body):
    depth = 1 if slug else 0
    p = '../' * depth
    return f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<script>document.documentElement.classList.add('js')</script>
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="noindex,nofollow">
<meta name="theme-color" content="#071A3A">
<link rel="icon" href="/assets/icons/favicon.ico" sizes="any">
<link rel="preload" href="/assets/fonts/archivo-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/anteprima/anteprima.css?v={V}">
<script src="/assets/vendor/gsap.min.js" defer></script>
<script src="/assets/vendor/ScrollTrigger.min.js" defer></script>
<script src="/assets/vendor/SplitText.min.js" defer></script>
<script src="/anteprima/anteprima.js?v={V}" defer></script>
</head>
<body>
<a class="skip" href="#main">Vai al contenuto</a>
{header(p, slug)}
<main id="main">
{body}
</main>
{footer(p)}
</body>
</html>
'''


def main():
    cards = json.load(open(os.path.join(SRC, 'agents.json')))
    grid = ''
    for key, name, intro in CATS:
        mine = [c for c in cards if f'data-cat="{key}"' in c]
        grid += f'''<section class="cat" id="{key}"><div class="wrap">
  <header class="cat-h"><h2>{name}</h2><p>{intro}</p><span class="cat-n">{len(mine)}</span></header>
  <ol class="agents-grid">{''.join(mine)}</ol>
</div></section>
'''
    for slug, src, title, desc, _ in PAGES:
        body = open(os.path.join(SRC, src)).read()
        p = '../' if slug else ''
        body = body.replace('{{AGENTS}}', ''.join(cards)).replace('{{AGENTS_GRID}}', grid).replace('{{P}}', p)
        path = page_path(slug)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w').write(layout(slug, title, desc, body.strip()))
    print(f'Anteprima: {len(PAGES)} pagine in {OUT}')


if __name__ == '__main__':
    main()
