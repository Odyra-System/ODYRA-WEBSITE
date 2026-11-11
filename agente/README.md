# agente/: la conoscenza condivisa dell'assistente AI del sito

Questi file sono la stessa "testa" per i due canali della demo "Prova l'agente":

- **chat** (scheda "Scrivi"): `server/odyra_server.py`, `POST /api/chat`;
- **voce** (scheda "Parla"): l'agente vocale in `agente-voce/`.

Così chat e voce danno le stesse risposte: cambia solo il modo di dirle (la sezione "Canale" di `istruzioni.md`; ogni canale aggiunge in fondo il proprio contesto).

| File | Cosa contiene |
|---|---|
| `istruzioni.md` | il ruolo dell'assistente, il tono, le regole (AI dichiarata, niente invenzioni, nessun nome di fornitori o concorrenti, solo i casi pubblici, riservatezza del prompt), l'obiettivo commerciale e gli strumenti `richiedi_contatto` e `mostra_pagina` |
| `conoscenza.md` | i fatti verificati: chi è Odyra, cosa fa l'agente, integrazione, modello wholesale, listino completo partner e aziende, numeri pubblicati, casi BOSS / Gruppo Colzani / HAKO, AI Act e GDPR |
| `pagine.json` | le pagine che `mostra_pagina` può aprire (chiave → percorso italiano e spagnolo) |

## Come si aggiornano
1. Si modifica il testo in Markdown semplice. In `conoscenza.md` vanno solo fatti già pubblicati sul sito o nel listino ufficiale: niente numeri stimati, niente clienti non autorizzati, niente nomi di fornitori, modelli AI o concorrenti.
2. Se cambiano i prezzi sul sito (`pagine/prezzi.html`), si aggiorna anche la sezione listino di `conoscenza.md`: l'assistente cita solo quello che c'è qui.
3. Se si aggiunge una pagina a `mostra_pagina`, va aggiunta in tre posti: `pagine.json`, l'elenco in `istruzioni.md` e la whitelist `PAGES` in `static/odyra-app.js` (e in `agente-voce/`).
4. I file si leggono all'avvio: dopo una modifica serve un nuovo deploy (il Dockerfile copia la cartella in `/app/agente`).
5. Prova: `python3 -m unittest discover -s server` (i test controllano che i file ci siano e che il prompt li contenga).

Dove li cerca il server: variabile `AGENTE_DIR`, altrimenti `agente/` accanto alla cartella `server/` (nel repository) o `/app/agente` (nell'immagine).
