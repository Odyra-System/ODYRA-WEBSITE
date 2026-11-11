#!/bin/sh
# Avvio del container: server delle API in background (riavviato se cade) e nginx in primo piano.
set -eu
: "${PORT:=8080}"
export PORT

# nginx.conf è un modello: si sostituisce solo ${PORT}, le variabili di nginx ($uri, $host...) restano.
# Tutto ciò che nginx scrive sta in /tmp: il container funziona con qualunque utente senza privilegi.
mkdir -p /tmp/nginx
envsubst '${PORT}' < /etc/nginx/templates/odyra.conf.template > /tmp/nginx/odyra.conf
nginx -t -q

# Supervisione semplice: se il server delle API si ferma, riparte dopo 2 secondi.
(
  while true; do
    python3 -u /app/server/odyra_server.py || true
    echo "odyra-api: processo terminato, riavvio tra 2 secondi" >&2
    sleep 2
  done
) &

exec nginx -g 'daemon off;'
