# 1) Genera il sito con build.py e prova il server delle API (solo libreria standard).
FROM python:3.12-alpine AS build
WORKDIR /src
COPY build.py ./
COPY pagine ./pagine
COPY static ./static
COPY server ./server
RUN python3 build.py && python3 -m unittest discover -s server

# 2) nginx serve il sito e passa /api/ al server Python su 127.0.0.1:8090. PORT arriva da Railway.
FROM nginx:1.27-alpine
RUN apk add --no-cache python3 \
 && rm -f /etc/nginx/conf.d/default.conf \
 && rm -rf /usr/share/nginx/html/* \
 && sed -i -e '/^user /d' -e 's#^pid .*#pid /tmp/nginx.pid;#' \
      -e 's#include /etc/nginx/conf.d/\*.conf;#include /tmp/nginx/odyra.conf; client_body_temp_path /tmp/nginx/body; proxy_temp_path /tmp/nginx/proxy; fastcgi_temp_path /tmp/nginx/fastcgi; uwsgi_temp_path /tmp/nginx/uwsgi; scgi_temp_path /tmp/nginx/scgi;#' /etc/nginx/nginx.conf \
 && grep -q 'include /tmp/nginx/odyra.conf' /etc/nginx/nginx.conf \
 && mkdir -p /app/server \
 && chown -R nginx:nginx /var/cache/nginx /etc/nginx/conf.d
ENV PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1 \
    API_HOST=127.0.0.1 \
    API_PORT=8090
COPY nginx.conf /etc/nginx/templates/odyra.conf.template
COPY server/odyra-headers.conf /etc/nginx/odyra-headers.conf
COPY server/odyra_server.py server/entrypoint.sh /app/server/
COPY --from=build /src/dist /usr/share/nginx/html
USER nginx
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -q -O /dev/null "http://127.0.0.1:${PORT}/api/salute" || exit 1
ENTRYPOINT ["/app/server/entrypoint.sh"]
