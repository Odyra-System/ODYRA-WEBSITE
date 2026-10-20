# Odyra System: sito

Sito statico bilingue (italiano in radice, spagnolo in `/es/`), pensato per essere letto bene da persone, motori di ricerca e assistenti AI.

    python3 build.py      # genera dist/ (solo libreria standard)

Il Dockerfile genera `dist/` e lo serve con nginx: non serve fare commit di `dist/`.

## Struttura
- `build.py`: tutti i testi e le pagine. Testi affiancati con `t('italiano', 'español')`. In cima: dominio, e-mail, dati societari, `UPDATED` (data dell'ultimo aggiornamento), link a HAKO e BOSS.
- `static/`: CSS, JS, carattere (Schibsted Grotesk, ospitato qui, licenza OFL), loghi, immagini.
- `nginx.conf`: indirizzi puliti, redirect 301 dai vecchi `.html`, Markdown su richiesta.

## Cosa esce per i crawler AI
- Ogni pagina ha la versione Markdown allo stesso indirizzo con `.md` (es. `/piattaforma.md`). Chi chiede `Accept: text/markdown` la riceve direttamente.
- `/llms.txt` (indice e fatti chiave) e `/llms-full.txt` (testo completo, it + es).
- JSON-LD in ogni pagina: Organization, WebSite, WebPage con breadcrumb, Service, SoftwareApplication (GoAgent), FAQPage.
- `robots.txt` con i bot AI ammessi esplicitamente; `sitemap.xml` con hreflang.
- Contenuto tutto nell'HTML, nessun testo che dipende da JavaScript.

## Quando cambi i contenuti
Aggiorna `UPDATED` in `build.py`. Le domande frequenti stanno in `faq_home()`, `faq_partner()` e `faq_all()`.

## Video
Metti `NOME.mp4` in `static/assets/video/` (opzionale `NOME.jpg` come anteprima e sottotitoli `NOME.it.vtt`, `NOME.es.vtt`, …) e rigenera: il video compare con i suoi dati strutturati. Nomi previsti: `partner-program` (pagina partner), `goagent` (pagina GoAgent). Senza file non compare nessun segnaposto.

## Da completare
- `FORM_ENDPOINT` in `static/script.js`: finché è vuoto il modulo apre la posta con la richiesta già scritta.
- Confermare gli indirizzi di BOSS (`LINK_BOSS`) e la frase sulla convention di ottobre 2026.
- Ok di Gruppo Colzani per citare nome, Sportit.com e Global Trading.
- Informativa privacy: bozza da far rivedere a un legale.
