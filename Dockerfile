# 1) Genera il sito con build.py (solo libreria standard).
FROM python:3.12-alpine AS build
WORKDIR /src
COPY build.py ./
COPY pagine ./pagine
COPY static ./static
RUN python3 build.py

# 2) Lo serve con nginx. PORT arriva dall'ambiente (Railway).
FROM nginx:1.27-alpine
ENV PORT=8080
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=build /src/dist /usr/share/nginx/html
