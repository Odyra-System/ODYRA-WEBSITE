# agente-voce: l'agente vocale del sito ("Prova l'agente" → "Parla")

Worker che risponde a voce ai visitatori del sito, dal browser. Nome dell'agente: `odyra_web`
(deve essere uguale a `VOICE_AGENT_NAME` del servizio del sito, che crea il token in `/api/voce`).

| File | Cosa fa |
|---|---|
| `agent.py` | il worker: motori di ascolto, ragionamento e voce, saluto con avviso AI, strumenti, controlli di silenzio e durata, chiusura della stanza |
| `core.py` | la logica senza dipendenze: caricamento del prompt, regole per la voce, pagine ammesse, controllo dei contatti, lingue, testi fissi |
| `test_agent.py` | prove senza rete e senza chiavi |
| `requirements.txt` | versioni fissate |
| `Dockerfile` | immagine per Railway (si costruisce dalla radice del repository) |

## Il prompt: uno solo per chat e voce
Il prompt è `agente/istruzioni.md` + `agente/conoscenza.md` (gli stessi file della chat del sito) + le
regole per la voce scritte in `core.py` (`REGOLE_VOCE`: frasi brevi, numeri a parole, niente elenchi, niente
link letti: si usa `mostra_pagina`) + il contesto (canale voce, data e ora, lingua del sito).

**Per cambiare cosa dice l'agente si modificano i file in `agente/`: vale per chat e voce insieme.**
Poi si fa un nuovo deploy di entrambi i servizi (i file si leggono all'avvio).
Le regole in `core.py` si toccano solo per cose che riguardano il parlato.

Dove cerca i file: variabile `AGENTE_DIR`; altrimenti `agente/` accanto ad `agent.py` (nell'immagine
`/app/agente`) o `../agente/` (nel repository). Se mancano, parte con un prompt di riserva prudente e
scrive nel log `prompt condiviso incompleto`: va corretto subito.

## Strumenti
- `richiedi_contatto(nome, telefono, email, azienda, interesse)`: controlla i dati (nome e almeno un
  recapito valido; l'email dettata a voce, "mario punto rossi chiocciola gmail punto com", viene
  ricomposta) e fa `POST` a `SITE_LEAD_URL` (predefinito `https://odyrasystemautomation.it/api/voce/lead`)
  con l'intestazione `X-Odyra-Secret: <VOICE_LEAD_SECRET>`, timeout 8 secondi.
  Corpo (stessi campi di `/api/contatto`, senza privacy né honeypot):
  `{name, email, phone, company, need, message, lang, page?}` con nome→name, telefono→phone,
  azienda→company, interesse→need; `message` è una nota fissa ("contatto raccolto dall'assistente vocale,
  confermato a voce"); `page` è l'ultima pagina aperta con `mostra_pagina`, se c'è.
  Se `VOICE_LEAD_SECRET` manca, non invia nulla: scrive nel log solo `lead ricevuto (nessuna destinazione
  configurata)` e l'agente invita a prenotare la call (apre `/prenota`). Lo stesso se l'invio fallisce.
- `mostra_pagina(pagina)`: manda `{"action":"navigate","path":...}` sul topic `ui` della stanza; il sito
  cambia pagina senza far cadere la chiamata. Chiavi e percorsi (italiano):

  | chiave | percorso |
  |---|---|
  | home | `/` |
  | prezzi | `/prezzi` |
  | partner | `/partner` |
  | prenota | `/prenota` |
  | casi | `/lavori` |
  | boss | `/case/boss-italia` |
  | tecnologie | `/tecnologie` |
  | contatti | `/contatti` |

  Se c'è `agente/pagine.json` (condiviso con la chat) si usa il percorso nella lingua del visitatore
  (per lo spagnolo, per esempio `/es/socios`). Il file non può aggiungere pagine: le chiavi ammesse sono
  solo queste otto. Una pagina nuova va aggiunta in `core.PAGINE`, `agente/pagine.json`,
  `agente/istruzioni.md` e nella whitelist di `static/odyra-app.js`.

## Variabili per il nuovo servizio Railway

Obbligatorie:

| Variabile | Note |
|---|---|
| `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` | lo stesso progetto usato dal sito per il token |
| `LIVEKIT_AGENT_NAME` | `odyra_web` (uguale a `VOICE_AGENT_NAME` del sito) |
| `DEEPGRAM_API_KEY` | ascolto |
| `OPENAI_API_KEY` | ragionamento (predefinito) |
| `INWORLD_API_KEY` + `INWORLD_VOICE` | voce (predefinita). Senza `INWORLD_VOICE` usa la voce di serie |
| `VOICE_LEAD_SECRET` | lo stesso valore della variabile omonima del servizio del sito. Senza, i contatti non si registrano (si invita a prenotare) |

Facoltative (con il valore predefinito):

| Variabile | Predefinito | Note |
|---|---|---|
| `ANTHROPIC_API_KEY` | – | se c'è, fa da riserva del ragionamento |
| `LLM_PROVIDER` | `openai` | `openai` o `anthropic` (l'altro, se ha la chiave, è la riserva) |
| `OPENAI_MODEL` (o `LLM_MODEL`) | `gpt-4.1-mini` | |
| `ANTHROPIC_MODEL` (o `LLM_FALLBACK_MODEL`) | `claude-sonnet-4-6` | |
| `LLM_FALLBACK_ENABLED`, `LLM_ATTEMPT_TIMEOUT_S`, `LLM_TEMPERATURE` | `true`, `3.0`, `0.4` | |
| `TTS_PROVIDER` | `inworld` | `inworld` o `cartesia` |
| `CARTESIA_API_KEY`, `CARTESIA_VOICE`, `CARTESIA_MODEL` | –, –, `sonic-3` | per `TTS_PROVIDER=cartesia` o per la riserva |
| `TTS_FALLBACK_ENABLED` | `false` | riserva della voce; spenta perché con la riserva la voce principale passava a una modalità che restava muta |
| `INWORLD_MODEL`, `INWORLD_SPEAKING_RATE`, `INWORLD_DELIVERY_MODE` | `inworld-tts-2`, `1.1`, `CREATIVE` | |
| `DEEPGRAM_MODEL`, `DEEPGRAM_LANGUAGE` | `nova-3-general`, automatico | automatico = `multi` per it/en/es/fr/de, monolingua per pl/ro |
| `SITE_LEAD_URL` | `https://odyrasystemautomation.it/api/voce/lead` | per le prove: `http://localhost:8090/api/voce/lead` |
| `DEFAULT_LANG` | `it` | se il token non porta la lingua (`it`, `es` o `en`) |
| `MAX_DURATION_S`, `SILENCE_TIMEOUT_S`, `STUCK_TIMEOUT_S` | `480`, `60`, `18` | |
| `TURN_DETECTION` | `model` | `vad` se ci sono silenzi su risposte brevi |
| `MIN_ENDPOINTING_DELAY`, `MAX_ENDPOINTING_DELAY`, `PREEMPTIVE_GENERATION`, `MIN_INTERRUPTION_DURATION`, `MIN_INTERRUPTION_WORDS`, `FALSE_INTERRUPTION_TIMEOUT_S`, `VAD_ACTIVATION_THRESHOLD`, `FILLER_DELAY_S`, `LANG_SWITCH_CONFIRMATIONS` | `0.3`, `1.5`, `true`, `0.6`, `2`, `2.0`, `0.5`, `0.7`, `2` | tempi di turno, come il worker attuale |
| `AVATAR_ENABLED` + `TAVUS_API_KEY`, `TAVUS_REPLICA_ID`, `TAVUS_PERSONA_ID` | `false` | avatar video; aggiunge latenza |
| `SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `SENTRY_RELEASE`, `SENTRY_TRACES_SAMPLE_RATE` | –, –, –, `0` | errori; senza dati della conversazione |
| `LOG_LEVEL`, `AGENTE_DIR` | `INFO`, automatico | |

Non servono più: `RAG_URL`, `CORE_BASE_URL`, `ODYRA_TENANT_ID`, `ODYRA_EOC_URL`, `FIRST_MESSAGE*`, `LEAD_WEBHOOK_URL`
(la conoscenza ora è in `agente/conoscenza.md`, il saluto è fisso in `core.py` con l'avviso AI).

## Lingue
L'agente parla italiano, spagnolo e inglese, come le istruzioni condivise. Il token del sito può portare
anche fr/de/pl/ro: in quel caso l'agente saluta e risponde in inglese, ma il riconoscimento della voce
resta nella lingua del sito (così capisce il visitatore). A metà conversazione segue il cambio tra
it/es/en dopo due frasi di fila nella nuova lingua; se rileva un'altra lingua passa all'inglese.

## Deploy su Railway (nuovo servizio in ODYRA CORE)
1. Nuovo servizio dal repository del sito, ramo `main` (o `develop` per le prove).
2. Settings → Source: **Root Directory vuota** (la radice: l'immagine deve vedere `agente/` e `agente-voce/`).
3. Settings → Build: builder Dockerfile, **Dockerfile Path = `agente-voce/Dockerfile`**.
   Facoltativo: Watch Paths `agente/**` e `agente-voce/**`, così i cambi al solo sito non lo ricostruiscono.
4. Variabili: quelle obbligatorie sopra.
5. Nessun dominio pubblico e nessuna porta: il worker si collega lui a LiveKit.
6. Dopo il primo avvio nei log deve comparire `pronto: agent=odyra_web ...` e `registered worker`.
   Poi si prova "Parla" sul sito. Quando funziona, si spegne il vecchio servizio "ODYRA WEBSITE AGENT"
   (finché sono accesi tutti e due con lo stesso nome agente, LiveKit manda le chiamate a uno dei due a caso).

Il `railway.toml` non si usa apposta: alla radice varrebbe anche per il servizio del sito.

## Prove in locale
```bash
cd agente-voce
python3.11 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python -m unittest -v test_agent          # senza chiavi e senza rete
python agent.py download-files            # una volta
# con le chiavi in agente-voce/.env (mai nel repository):
python agent.py console                   # parli dal microfono del computer, senza sito
python agent.py dev                       # si registra su LiveKit: lo provi da "Parla" del sito in locale
```
Con `dev` usare un `LIVEKIT_AGENT_NAME` diverso (es. `odyra_web_dev`) e lo stesso valore in
`VOICE_AGENT_NAME` del sito locale, per non rubare le chiamate alla produzione.

Solo le prove su `core.py` girano senza pacchetti (`python3 -m unittest test_agent`: le altre vengono saltate).

## Aggiornare le versioni
`livekit-agents` e i plugin restano a 1.6.1 come i worker in produzione (con 1.6.5 la voce Inworld
restava muta). `anthropic`, `openai` e `httpx` sono fissati perché i plugin 1.6.1 non li limitano: senza
pin pip installa `anthropic` 2.x e la riserva del ragionamento si rompe all'avvio. Prima di aggiornare:
venv nuovo, test, poi una prova vocale vera con `console`.

## Privacy nei log
Nei log ci sono solo eventi tecnici (lingua, motivo di chiusura, esito HTTP del lead). Mai trascrizioni,
nomi, numeri, email o metadati grezzi. Sentry, se attivo, riceve solo errori, senza variabili locali né dati
della richiesta. L'ascolto ha `mip_opt_out` attivo (l'audio non si usa per addestrare modelli del fornitore).
