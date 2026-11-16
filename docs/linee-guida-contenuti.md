# Linee guida dei contenuti del sito

Regole ricavate dall'analisi commerciale interna di novembre 2026 (documento riservato, **non** va caricato in questa repo: la repo è pubblica). Qui c'è solo ciò che riguarda il sito. Valgono per tutte le pagine (`pagine/`, `pagine/es/`), per i testi generati in `build.py` (FAQ, `llms.txt`) e per la conoscenza dell'assistente (`agente/`).

Il controllo automatico è in `server/test_contenuti.py` (gira nel build Docker: se una regola marcata **[test]** è violata, il deploy si ferma). Per una revisione completa usare l'agente `revisore-contenuti` (`.claude/agents/revisore-contenuti.md`).

## 1. Posizionamento e pubblici
1. Primo pubblico: **catene e gruppi multi-sede a gestione diretta** di servizi su appuntamento, che comprano direttamente da Odyra, sede per sede. Secondo pubblico: **software house** e gestionali verticali, che rivendono in white-label. La home, le soluzioni e i prezzi li presentano in quest'ordine. **[test: home e prezzi]**
2. Il messaggio è il **risultato in agenda** (chiamate risposte, appuntamenti scritti nel gestionale, richiamate fatte), non la tecnologia e non i minuti.
3. Una **rete di affiliati non è una catena**: ogni sede ha la propria agenda e decide se aderire. Non promettere a un franchising quello che vale per una catena diretta; dire che si parte da un accordo con la casa madre, meglio se c'è un numero unico o un'agenda comune.
4. Ordine dei verticali da mostrare: studi dentistici; centri estetici ed epilazione; poliambulatori; assistenza delle concessionarie; cliniche veterinarie. Il beauty è l'unico in produzione: dirlo. Palestre e centri sportivi non sono un verticale prioritario.

## 2. Offerta d'ingresso
1. Per i gruppi la proposta principale è l'**audit gratuito delle chiamate** (`/audit-chiamate`): due settimane, 3–5 sedi, nessun costo né impegno, report per sede con il metodo. Le CTA principali delle pagine per i gruppi puntano lì. **[test: la pagina esiste ed è linkata dalla home]**
2. Per le software house la proposta è la **beta gratuita su 5 centri per 60 giorni**, con i numeri del pilota prima dell'impegno.
3. Dopo l'audit si propone un pilota sulle sedi dove serve di più, misurato con gli stessi indicatori prima e dopo. Non scrivere che il pilota è gratuito o a pagamento finché non è deciso.

## 3. Prezzi
1. I prezzi si citano **solo dal listino** (`pagine/prezzi.html`, `agente/conoscenza.md`). Nessuna modifica di prezzi, taglie o condizioni senza decisione dei fondatori.
2. **Mai il prezzo al minuto come argomento di vendita** ("0,18 € al minuto" e simili): sul minuto Odyra perde il confronto. Gli extra a consumo al minuto si possono indicare come dettaglio del listino. **[test]**
3. L'offerta da mettere davanti è il **Combo** voce + WhatsApp (costi WhatsApp inclusi): nelle schede prezzi va per primo ed è marcato "Consigliato". **[test]**
4. Niente "WhatsApp illimitato" o "incluso senza limiti": i volumi sono quelli del pacchetto e le tariffe seguono quelle ufficiali WhatsApp. **[test]**

## 4. Affermazioni e prove
1. **BOSS / GoAgent**: GoAgent è in produzione da giugno 2026 dentro GoWeb, il gestionale che BOSS fornisce a oltre 1.500 saloni, ed è *offerto* a quei saloni. Non scrivere mai che lavora "su una rete di 1.500 saloni", che è "attivo su 1.500 saloni" o formule simili. **[test]**
2. **Nessuna percentuale di mercato sulle chiamate perse** ("perdete il 30% delle chiamate", "il 40% non va a buon fine"): non esiste un dato italiano verificato. Si misura sul cliente con l'audit. **[test]**
3. I soli numeri di risultato pubblicabili sono quelli misurati sugli agenti Odyra in produzione, con il metodo spiegato (`/lavori/risultati`). Niente ritorni dell'investimento promessi, niente "sostituisce il personale".
4. **Nessun nome di concorrente o fornitore** nelle pagine: i confronti sono per tipo di soluzione. Non affermare che un concorrente ha o non ha una funzione in Italia. **[test]**
5. Niente frasi assolute sul mercato ("unici in Italia", "nessuno lo fa", "canale libero").
6. Solo i casi pubblici: BOSS / GoAgent, Gruppo Colzani, HAKO. Nessun logo, testimonianza o cifra inventati.
7. AI Act: l'agente dice sempre di essere un'AI e passa a una persona quando serve. Va detto dove si parla di voce.

## 5. SEO
1. Titolo ≤ 70 caratteri, descrizione 70–160 caratteri, in italiano naturale. **[test]**
2. Parole chiave con domanda reale, una pagina per gruppo:
   - home: segretaria AI + centralino AI per gruppi multi-sede;
   - `/centralino-ai`: centralino AI, centralino intelligenza artificiale;
   - `/segretaria-ai`: segretaria AI, segreteria telefonica AI, segretaria virtuale AI, assistente/agente/receptionist AI;
   - `/segretaria-virtuale`: segretaria virtuale (confronto operatore vs AI);
   - `/risponditore-automatico`: risponditore automatico (confronto IVR vs agente);
   - `/promemoria-whatsapp`: messaggi automatici WhatsApp Business, promemoria appuntamenti, chatbot WhatsApp Business;
   - `/settori/centri-estetici`, `/settori/studi-dentistici`: marketing centro estetico / studio dentistico, gestione agenda;
   - `/partner`: white label AI (per credibilità in trattativa, non per traffico).
3. Da non inseguire: "segreteria virtuale" generica, "centralino virtuale", "centralino cloud", "ivr", "chatbot ai", "agenti ai", "chiamate perse" (intento privato), "prenotazione visite online", "whatsapp business api", e i nomi dei gestionali (sono i nostri clienti potenziali).
4. Ogni pagina nuova va nel piede (`FOOTER` in `build.py`) o linkata da una pagina madre, con `parent:` nel commento iniziale.
5. La demo vocale (`data-voice-demo`) resta raggiungibile da tutte le pagine.
