# Sito Odyra: istruzioni per Claude

- Prima di toccare testi, prezzi o pagine leggi `docs/linee-guida-contenuti.md`: sono le regole commerciali del sito (posizionamento, offerta, affermazioni ammesse, SEO). Valgono alla lettera.
- L'analisi commerciale da cui vengono è riservata: non copiarla nella repo, che è pubblica (niente margini, lead, nomi di persone, email).
- Dopo ogni modifica ai contenuti: `python3 build.py` e `python3 -m unittest discover -s server`, poi fai rivedere il lavoro all'agente `revisore-contenuti` e correggi ciò che segnala prima del commit.
- Prezzi, taglie e condizioni si cambiano solo su decisione dei fondatori.
- Ogni testo esiste in italiano e, se la pagina c'è, in spagnolo: tienili allineati.
- Il resto (struttura, build, API, deploy) è nel `README.md`.
