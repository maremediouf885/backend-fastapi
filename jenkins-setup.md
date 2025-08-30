# Configuration Jenkins CI/CD

## 1. Accéder à Jenkins
- URL: http://localhost:8081
- Mot de passe initial: `365ed83397a2401f84b4f80aaac25e8c`

## 2. Installer les plugins nécessaires
Dans Jenkins → Manage Jenkins → Plugins:
- **Docker Pipeline**
- **Git**
- **Pipeline**
- **Credentials Binding**

## 3. Configurer les credentials
Dans Jenkins → Manage Jenkins → Credentials → Global:

### Docker Hub Credentials
- Kind: Username with password
- ID: `docker-hub-credentials`
- Username: `maremediouf885`
- Password: [ton mot de passe Docker Hub]

## 4. Créer le job Pipeline
1. New Item → Pipeline
2. Nom: `transfert-denrees-pipeline`
3. Pipeline → Definition: Pipeline script from SCM
4. SCM: Git
5. Repository URL: `https://github.com/maremediouf885/backend-fastapi.git`
6. Branch: `*/main`
7. Script Path: `Jenkinsfile`

## 5. Déclencher le build
- Build Now
- Ou automatiquement sur push GitHub (webhook)

## 6. Étapes du pipeline
1. **Checkout** - Récupération du code
2. **Install Dependencies** - Installation Python
3. **Run Tests** - Tests unitaires
4. **Build Docker Image** - Construction image
5. **Push to Registry** - Publication Docker Hub
6. **Deploy** - Déploiement local

## 7. Monitoring
- Console Output pour voir les logs
- Blue Ocean pour interface moderne
- Build History pour historique