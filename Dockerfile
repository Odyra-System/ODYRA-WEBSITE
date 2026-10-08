FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY *.html styles.css script.js manifest.webmanifest robots.txt sitemap.xml /usr/share/nginx/html/
COPY es /usr/share/nginx/html/es
COPY proposte /usr/share/nginx/html/proposte
COPY assets /usr/share/nginx/html/assets
