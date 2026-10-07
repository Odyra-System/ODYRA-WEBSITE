# Odyra System — sito

Sito statico bilingue (italiano in radice, spagnolo in `/es/`). Le pagine si generano da `build.py`:

    python3 build.py

Testi affiancati con `t('italiano','español')`. Indirizzi dei siti prodotto in cima a `build.py` (`LINK_HAKO`, `LINK_BOSS`, `LINK_GOAGENT`).

## Video (segnaposto già pronti)
Metti i file in `assets/video/`: il segnaposto viene sostituito da solo.
- `odyra-presentazione.mp4` (home), `partner-program.mp4` (pagina gestionali), `goagent.mp4`, ` (non più usato)
- opzionale: `NOME.jpg` (anteprima)
- sottotitoli selezionabili dal lettore: `NOME.it.vtt`, `NOME.es.vtt`, `NOME.en.vtt`, `NOME.de.vtt`, `NOME.fr.vtt`. Nella pagina spagnola il sottotitolo spagnolo parte attivo.

## Da completare
- `FORM_ENDPOINT` in `script.js`: finché è vuoto il modulo apre la posta con la richiesta già scritta.
- Confermare gli indirizzi dei siti di BOSS e GoAgent e la data della convention (17-19 ottobre).
- Ok di Gruppo Colzani per nome e logo Sportit.
- `privacy.html`: bozza da far rivedere a un legale.
