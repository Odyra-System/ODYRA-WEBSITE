# Agente vocale del sito (odyra_web). Si costruisce dalla RADICE del repository:
#   docker build -f agente-voce/Dockerfile .
# Su Railway: Root Directory vuota (radice), Dockerfile path = agente-voce/Dockerfile.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AGENTE_DIR=/app/agente

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ \
 && rm -rf /var/lib/apt/lists/*

COPY agente-voce/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Istruzioni e conoscenza condivise con la chat del sito, poi il codice dell'agente.
COPY agente/ /app/agente/
COPY agente-voce/core.py agente-voce/agent.py /app/

# Utente senza privilegi; i modelli locali (rilevamento della voce) si scaricano in build
# per evitare l'attesa al primo collegamento.
RUN useradd --create-home --uid 10001 odyra && chown -R odyra /app
USER odyra
RUN python agent.py download-files

CMD ["python", "agent.py", "start"]
