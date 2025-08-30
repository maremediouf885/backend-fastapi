# 1. Utiliser une image Python légère
FROM python:3.11-slim

# 2. Définir le dossier de travail dans le conteneur
WORKDIR /app

# 3. Copier uniquement requirements pour profiter du cache
COPY requirements.txt .

# 4. Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copier tout le code dans le conteneur
COPY . .

# 6. Exposer le port
EXPOSE 8000

# 7. Lancer l'application avec uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]