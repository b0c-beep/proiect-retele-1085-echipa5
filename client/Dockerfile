# Imaginea de baza - Python 3.10 in varianta slim (fara pachete inutile, mai mica)
FROM python:3.10-slim

# Setam directorul de lucru in container. Toate fisierele vor fi copiate aici.
WORKDIR /app

# Copiem toate fisierele clientului din contextul de build in /app.
# Contextul de build este radacina proiectului (definita in docker-compose.yml).
COPY client/main.py client/commands.py client/handlers.py client/connection.py client/state.py client/executor.py client/protocol.py ./

# Copiem si scripturile pe care clientul le poate expune in retea
COPY scripts/ ./scripts/

# Comanda rulata cand containerul porneste - lanseaza shell-ul interactiv al clientului
CMD ["python", "main.py"]
