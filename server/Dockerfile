# Imaginea de baza - Python 3.10 in varianta slim (fara pachete inutile, mai mica)
FROM python:3.10-slim

# Setam directorul de lucru in container. Toate fisierele vor fi copiate aici.
WORKDIR /app

# Copiem toate fisierele serverului din contextul de build in /app.
# Contextul de build este radacina proiectului (definita in docker-compose.yml).
COPY server/main.py server/handlers.py server/pipeline.py server/cli.py server/state.py server/protocol.py ./

# Variabile de mediu - pot fi suprascrise din docker-compose.yml sau la rulare
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=8506

# Declaram portul pe care serverul asculta conexiuni TCP
EXPOSE 8506

# Comanda rulata cand containerul porneste
CMD ["python", "main.py"]
