# Odyra System — sito di gruppo

Sito statico bilingue (italiano in radice, spagnolo in `/es/`). Nessuna build lato server.

## Modificare i contenuti
Le pagine sono generate da `build.py` (testi affiancati con `t('italiano','español')`):

    python3 build.py

Pubblicazione: Cloudflare Pages (nessun build command, output `/`) oppure `Dockerfile` con nginx.

## Da completare
- `FORM_ENDPOINT` in `script.js`: finché è vuoto il modulo apre la posta con la richiesta già scritta; incollare il webhook n8n per inviare i dati.
- Video: `assets/video/manifesto-odyra.mp4` (+ `.jpg`): la sezione compare da sola.
- Registrazioni reali: audio in `assets/audio/` + `chiamate.json` `[{"file":"x.mp3","titolo":"…","titolo_es":"…"}]`: la sezione "Ascolta" compare da sola.
- Loghi ufficiali mancanti: Global Trading / Sportit e GoAgent (ora wordmark con la "G" del pannello GoAgent) in `assets/logos/`.
- `privacy.html`: bozza da far rivedere a un legale.
