# Odyra System: sito

Sito statico bilingue (italiano in radice, spagnolo in `/es/`, stesso design), pensato per essere letto bene da persone, motori di ricerca e assistenti AI.

    python3 build.py      # genera dist/ (solo libreria standard)

Il Dockerfile genera `dist/` e lo serve con nginx: non serve fare commit di `dist/`.

## Struttura
- `pagine/` (italiano) e `pagine/es/` (spagnolo): le pagine, solo il contenuto di `<main>`, con gli stessi nomi di file e lo stesso markup. `agents.json` è il catalogo degli agenti. Quando cambi una pagina italiana, cambia anche la spagnola.
- `build.py`: genera tutto. In cima: dominio, e-mail, dati societari, `UPDATED` (data dell'ultimo aggiornamento). `PAGES` e `TEXT` danno per ogni lingua indirizzo, titolo e descrizione; `UI` i testi di testata e piede. Domande frequenti e privacy sono generate qui (`faq_all()`, `body_privacy()`), con i testi affiancati `t('italiano', 'español')`.
- `static/`: `odyra.css` e `odyra.js` (i pochi testi del JavaScript seguono la lingua della pagina), caratteri ospitati qui (licenza OFL), loghi, immagini, GSAP.

## Foto e video
Nelle pagine ci sono riquadri "da caricare" (video di presentazione, foto dei progetti, foto del team). `build.py` li nasconde finché sono vuoti: per pubblicare una foto o un video sostituisci il riquadro con il contenuto vero e rigenera.
- `nginx.conf`: indirizzi puliti, redirect 301 dai vecchi `.html`, Markdown su richiesta.

## Cosa esce per i crawler AI
- Ogni pagina ha la versione Markdown allo stesso indirizzo con `.md` (es. `/piattaforma.md`). Chi chiede `Accept: text/markdown` la riceve direttamente.
- `/llms.txt` (indice e fatti chiave) e `/llms-full.txt` (testo completo, it + es).
- JSON-LD in ogni pagina: Organization, WebSite, WebPage (AboutPage, ContactPage, FAQPage) con breadcrumb.
- `robots.txt` con i bot AI ammessi esplicitamente; `sitemap.xml` con hreflang.
- Contenuto tutto nell'HTML, nessun testo che dipende da JavaScript.

## Quando cambi i contenuti
Aggiorna `UPDATED` in `build.py`. Le domande frequenti stanno in `faq_home()`, `faq_partner()` e `faq_all()`.

## Foto e video da inserire
I riquadri "da caricare" / "pendiente de subir" (video di presentazione, foto dei progetti, del team e dei workshop) sono nelle pagine ma `build.py` non li pubblica finché sono vuoti. Metti i file in `static/assets/img/` o `static/assets/video/`, sostituisci il riquadro con l'immagine o il video in entrambe le lingue e rigenera.

## Da completare
- `FORM_ENDPOINT` in `static/odyra.js`: finché è vuoto il modulo apre la posta con la richiesta già scritta.
- Ok di Gruppo Colzani per citare nome, Sportit.com e Global Trading.
- Informativa privacy: bozza da far rivedere a un legale.
