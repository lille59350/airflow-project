# Image Python légère
FROM python:3.12-slim

# Répertoire de travail dans le conteneur
WORKDIR /app

# Installation des dépendances Python
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copie du code de notre API
COPY main.py .

# Documentation du port utilisé
EXPOSE 8000

# Démarrage de l'application FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]