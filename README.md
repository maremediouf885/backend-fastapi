# API Transfert de Denrées Alimentaires

API FastAPI pour la gestion des transferts de denrées alimentaires avec authentification JWT et base PostgreSQL.

## Fonctionnalités

- **Authentification** : JWT avec gestion des utilisateurs
- **Offres** : Gestion des offres de denrées
- **Transactions** : Suivi des transferts
- **Administration** : Panel d'administration

## Docker

### Lancement rapide
```bash
docker-compose up -d
```

### Pipeline CI/CD
```bash
# Tests unitaires
pytest tests/ -v

# Pipeline complet
test-pipeline.bat
```

## Documentation

- **API Docs** : http://localhost:8000/docs
- **Status** : http://localhost:8000/status

## Technologies

- FastAPI
- PostgreSQL
- Docker & Docker Compose
- JWT Authentication
- Pytest
- GitHub Actions CI/CD