# Odyra System: sito

Sito statico bilingue (italiano in radice, spagnolo in `/es/`, stesso design), pensato per essere letto bene da persone, motori di ricerca e assistenti AI. Un piccolo server Python (solo libreria standard) gestisce il modulo contatti e la demo vocale.

    python3 build.py                              # genera dist/ (solo libreria standard)
    ODYRA_DIST=/tmp/prova python3 build.py        # stessa cosa in un'altra cartella
    python3 -m unittest discover -s server -v     # test del server delle API

Il Dockerfile genera `dist/`, esegue i test del server e serve tutto con nginx: non serve fare commit di `dist/`.

## Struttura
- `pagine/` (italiano, anche in sottocartelle) e `pagine/es/` (spagnolo): le pagine, solo il contenuto di `<main>`, con in cima il commento `<!--pagina ... -->` (id, slug, titolo, descrizione...). Stesso `id` in italiano e spagnolo = stessa pagina tradotta. Link interni sempre come `{{URL:id-pagina}}`. `agents.json` è il catalogo degli agenti.
- `build.py`: genera tutto. In cima: dominio, e-mail, dati societari, `UPDATED`. Le pagine "domande" e "privacy" sono generate qui (`faq_all()`, `body_privacy()`), con i testi affiancati `t('italiano', 'español')`. Scrive anche Markdown (`/pagina.md`), `llms.txt`, `llms-full.txt`, `sitemap.xml` (senza le pagine `noindex`), `robots.txt` (con `Disallow: /api/`).
- `static/`: `odyra.css` e `odyra.js` (grafica e movimento), `odyra-app.js` e `odyra-app.css` (consenso cookie, misurazione, modulo contatti, demo vocale), caratteri (licenza OFL), loghi, immagini, librerie in `assets/vendor/` (GSAP; `rtc-client.min.js` per la demo vocale, licenza Apache 2.0 in `rtc-client.LICENSE.txt`).
- `server/`: `odyra_server.py` (API), `test_server.py` (test), `entrypoint.sh` (avvio del container), `odyra-headers.conf` (intestazioni di sicurezza incluse da nginx).
- `nginx.conf`: modello con `${PORT}`. Indirizzi senza barra finale (`/partner/vantaggi` serve `partner/vantaggi/index.html`; `/partner/vantaggi/` fa 301 alla versione senza barra, tranne `/` e `/es/`), redirect 301 in un solo salto dai vecchi indirizzi, Markdown su richiesta (`Accept: text/markdown`), `/api/` verso il server Python, cache, gzip, pagine 404 in italiano e spagnolo.

## Container
Una sola immagine (`nginx:1.27-alpine` + `python3`), utente non root. `entrypoint.sh` scrive la configurazione di nginx con la porta di Railway (`$PORT`, predefinita 8080), avvia il server delle API su `127.0.0.1:8090` (riavviato in automatico se si ferma) e nginx in primo piano. Controllo di salute: `GET /api/salute` (anche da impostare come healthcheck su Railway).

## Variabili d'ambiente (Railway)
Le chiavi vanno solo nelle variabili del servizio, mai nel repository.

| Variabile | Serve a | Note |
|---|---|---|
| `RESEND_API_KEY` | e-mail del modulo tramite API HTTP | ha la precedenza su SMTP |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` | e-mail del modulo tramite SMTP, se manca la chiave API | porta 587 (predefinita) con STARTTLS obbligatorio se c'è l'utente; 465 = SSL |
| `MAIL_FROM` | mittente | predefinito `Odyra <noreply@odyrasystemautomation.it>` (il dominio deve essere verificato dal servizio e-mail) |
| `MAIL_TO` | chi riceve le richieste | predefinito `team@odyrasystemautomation.it` |
| `LEAD_WEBHOOK_URL` | facoltativo: POST JSON del lead (`source: "odyra_website_form"`) | |
| `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` | demo vocale nel browser | senza, la demo risponde "non disponibile" |
| `VOICE_AGENT_NAME` | facoltativo: nome dell'agente vocale | predefinito `odyra_web` |
| `ALLOWED_ORIGINS` | facoltativo: origini ammesse per le API, separate da virgola, ammesso `https://*.dominio` | predefinito: il dominio con e senza `www` e `https://*.up.railway.app` |

`GET /api/salute` dice cosa è configurato, senza valori: `{"ok":true,"contatto":true,"email":"api"|"smtp"|null,"webhook":false,"voce":true}`.

## API
- `POST /api/contatto` (JSON, massimo 16 KB, solo dalle origini ammesse, 5 richieste ogni 10 minuti per indirizzo IP): `name`, `email`, `company`, `phone`, `need`, `message`, `source`, `page`, `privacy: true`, `website` (campo trappola per i bot: se è pieno la risposta è 200 ma non parte nulla), `attribution` (parametri delle campagne). Invia l'e-mail al team (con la provenienza in fondo) e la conferma al visitatore, e il webhook se c'è. Risposte: 200 se almeno un canale ha funzionato, 400 dati non validi, 403 origine, 413, 415, 429, 502 se tutti i canali falliscono, 503 se non c'è nessun canale configurato (il sito allora apre la posta con la richiesta già scritta).
- `POST /api/voce/token` (`{"lang":"it"}`; lingue it, en, es, fr, de, pl, ro): token di 15 minuti per una stanza nuova, con l'agente vocale già assegnato. 5 richieste ogni 10 minuti per IP.
- Nei log del server solo esito e canale, mai dati personali.

## Modulo contatti (contratto per le pagine)
Ogni `form[data-lead-form]` viene gestito da `odyra-app.js`: campi `name`, `company`, `email`, `phone`, `need`, `message`, casella `privacy` obbligatoria, trappola `<input name="website" class="hp" tabindex="-1" autocomplete="off">`, stato `<p class="form-status" role="status" aria-live="polite">`, attributo `data-source` (nome del modulo) e facoltativo `data-redirect="/indirizzo"` dopo l'invio riuscito. Testi personalizzabili con `data-ok`, `data-mail`. Funziona anche il vecchio `#form-contatti` (campi `nome`, `azienda`, `telefono`, `messaggio`, `interesse`).

## Consenso e misurazione
- Google Consent Mode v2: tutto negato finché il visitatore non sceglie; poi il tag Google Ads `AW-18360673034`. Banner con "Accetta tutti", "Solo necessari", "Preferenze" (statistica = Microsoft Clarity, marketing = Google Ads); scelta in `localStorage` (`odyra-consent`). Qualunque elemento con `data-cookie-prefs` riapre il banner (nel piede c'è "Preferenze cookie").
- Eventi: `generate_lead` (invio riuscito), `voice_demo_start`, `click_demo` (link verso contatti/demo e pulsanti della demo vocale).
- Parametri delle campagne (gclid, wbraid, gbraid, msclkid, utm_*, ...) salvati per la sessione e allegati alla richiesta.
- Nessuno script in linea: la Content-Security-Policy li vieta. Se aggiungi un servizio esterno, aggiorna `server/odyra-headers.conf`.

## Demo vocale
Pulsante in basso a destra su tutte le pagine (nascosto mentre c'è il banner cookie e, su schermi piccoli, quando in basso ci sono altri pulsanti) e qualunque elemento con `data-voice-demo`. La libreria si carica solo al primo clic. Se l'agente porta il visitatore su un'altra pagina, cambia solo il contenuto di `<main>` (la chiamata non cade); se non riesce compare il link "Apri la pagina". Il server della demo deve stare su `*.livekit.cloud`, altrimenti va aggiunto il suo dominio a `connect-src` in `server/odyra-headers.conf`.

## Quando cambi i contenuti
Aggiorna `UPDATED` in `build.py`. Le domande frequenti stanno in `faq_home()`, `faq_partner()` e `faq_all()`.

## Foto e video da inserire
I riquadri "da caricare" / "pendiente de subir" sono nelle pagine ma `build.py` non li pubblica finché sono vuoti. Metti i file in `static/assets/img/` o `static/assets/video/`, sostituisci il riquadro con l'immagine o il video in entrambe le lingue e rigenera.

## Da completare
- Variabili d'ambiente su Railway (sopra) per modulo e demo vocale.
- Informativa privacy, cookie policy e termini: testi da far rivedere a un legale.
- Foto e schermate vere di Gruppo Colzani; foto dei workshop dell'Academy.
