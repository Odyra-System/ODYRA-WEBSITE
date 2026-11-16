"""Controlli automatici sui contenuti del sito (regole in docs/linee-guida-contenuti.md).

Genera il sito in una cartella temporanea e verifica le regole marcate [test]. Gira nel build
Docker insieme agli altri test: se una regola è violata, il deploy si ferma.
"""
import glob
import html
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Frasi vietate: (regola, espressione). Si cercano nel testo servito e nella conoscenza dell'assistente.
VIETATE = [
    ('prezzo al minuto come argomento di vendita', r'0,18\s*€\s*(al|el)\s+minuto'),
    ('1.500 saloni presentati come attivi', r'(su|in)\s+una\s+(rete|red)\s+di\s+(oltre|más\s+de)\s+1\.500'),
    ('1.500 saloni presentati come attivi', r'(attiv[oaie]|in\s+produzione|lavora)\s+(su|in)\s+(oltre\s+|più\s+di\s+)?1\.500'),
    ('1.500 saloni presentati come attivi', r'per\s+1\.500\+?\s+saloni'),
    ('WhatsApp illimitato', r'illimitat|ilimitad'),
    ('percentuale di mercato sulle chiamate perse', r'\d{1,2}\s?%\s+(delle|de\s+las)\s+(chiamate|llamadas)'),
    ('percentuale di mercato sulle chiamate perse', r'(perdete|perdono|pierden)\s+(il|el)\s+\d'),
    ('nome di concorrente o fornitore', r'\b(fonio|rispondo\.ai|aircall|cloudtalk|treatwell|miodottore|docplanner|ainora|keplero|yourang|elevenlabs|vapi|retell|synthflow|famulor)\b'),
    ('frase assoluta sul mercato', r'\b(unici in italia|unico in italia|nessuno in italia|canale libero)\b'),
]


class TestContenuti(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        env = dict(os.environ, ODYRA_DIST=cls.tmp.name)
        subprocess.run([sys.executable, os.path.join(ROOT, 'build.py')], cwd=ROOT, env=env, check=True,
                       stdout=subprocess.DEVNULL)
        cls.pagine = {}
        for f in glob.glob(os.path.join(cls.tmp.name, '**', 'index.html'), recursive=True):
            rel = os.path.relpath(f, cls.tmp.name)
            with open(f, encoding='utf-8') as fh:
                cls.pagine[rel] = fh.read()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @staticmethod
    def _testo(s):
        s = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', s, flags=re.S)
        return html.unescape(re.sub(r'<[^>]+>', ' ', s))

    def test_frasi_vietate_nelle_pagine(self):
        errori = []
        for rel, s in self.pagine.items():
            t = self._testo(s)
            for regola, rx in VIETATE:
                for m in re.finditer(rx, t, re.I):
                    errori.append(f'{rel}: {regola}: “{t[max(0, m.start() - 40):m.end() + 40].strip()}”')
        self.assertFalse(errori, '\n' + '\n'.join(errori))

    def test_frasi_vietate_nell_assistente(self):
        errori = []
        for nome in ('istruzioni.md', 'conoscenza.md'):
            with open(os.path.join(ROOT, 'agente', nome), encoding='utf-8') as fh:
                t = fh.read()
            for regola, rx in VIETATE:
                if regola == 'nome di concorrente o fornitore':
                    continue  # le istruzioni nominano categorie, non concorrenti; il controllo resta sulle pagine
                for m in re.finditer(rx, t, re.I):
                    errori.append(f'agente/{nome}: {regola}: “{t[max(0, m.start() - 40):m.end() + 40].strip()}”')
        self.assertFalse(errori, '\n' + '\n'.join(errori))

    def test_titoli_e_descrizioni(self):
        errori = []
        for rel, s in self.pagine.items():
            if 'noindex' in s[:3000] or rel.startswith('404'):
                continue
            t = html.unescape(re.search(r'<title>(.*?)</title>', s, re.S).group(1))
            d = html.unescape(re.search(r'<meta name="description" content="(.*?)"', s).group(1))
            if len(t) > 70:
                errori.append(f'{rel}: titolo di {len(t)} caratteri (max 70): {t}')
            if not 70 <= len(d) <= 160:
                errori.append(f'{rel}: descrizione di {len(d)} caratteri (70–160)')
            if len(re.findall(r'<h1\b', s)) != 1:
                errori.append(f'{rel}: serve un solo h1')
        self.assertFalse(errori, '\n' + '\n'.join(errori))

    def test_home_parla_prima_ai_gruppi(self):
        s = self.pagine['index.html']
        self.assertIn('gruppi multi-sede', html.unescape(re.search(r'<title>(.*?)</title>', s).group(1)))
        self.assertIn('href="/audit-chiamate"', s)
        self.assertLess(s.index('id="aziende"'), s.index('id="modello"'), 'i gruppi vanno prima delle software house')

    def test_audit_gratuito(self):
        s = self.pagine.get(os.path.join('audit-chiamate', 'index.html'))
        self.assertIsNotNone(s, 'manca la pagina /audit-chiamate')
        self.assertIn('data-lead-form', s)

    def test_prezzi_gruppi_e_combo_per_primi(self):
        s = self.pagine[os.path.join('prezzi', 'index.html')]
        self.assertLess(s.index('id="tab-aziende"'), s.index('id="tab-partner"'))
        for griglia in ('pz-cards', 'pz-pv-grid'):
            i = s.index(griglia)
            primo = re.search(r'<article class="([^"]*)"', s[i:]).group(1)
            self.assertIn('pz-card-combo', primo, f'nella griglia {griglia} il Combo va per primo')


if __name__ == '__main__':
    unittest.main()
