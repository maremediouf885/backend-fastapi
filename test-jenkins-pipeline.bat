@echo off
echo ========================================
echo   TEST PIPELINE JENKINS LOCAL
echo ========================================

echo.
echo [SIMULATION] Checkout du code...
echo Code récupéré depuis Git

echo.
echo [SIMULATION] Installation des dépendances...
pip install -r requirements.txt

echo.
echo [SIMULATION] Tests unitaires...
pytest tests/ -v --tb=short
if %errorlevel% neq 0 (
    echo ECHEC: Tests unitaires
    exit /b 1
)

echo.
echo [SIMULATION] Build Docker...
docker build -t transfert-denrees-api:jenkins-test .
if %errorlevel% neq 0 (
    echo ECHEC: Build Docker
    exit /b 1
)

echo.
echo [SIMULATION] Déploiement...
docker stop transfert-denrees-app 2>nul || echo Conteneur non trouvé
docker rm transfert-denrees-app 2>nul || echo Conteneur non trouvé
docker run -d --name transfert-denrees-app -p 8002:8000 ^
    -e DATABASE_URL="postgresql://postgres:passer123@host.docker.internal:5432/denrees_db" ^
    -e SECRET_KEY="your-secret-key-here" ^
    transfert-denrees-api:jenkins-test

echo.
echo [TEST] Vérification de l'API...
timeout /t 5
curl -f http://localhost:8002/status
if %errorlevel% equ 0 (
    echo SUCCÈS: API déployée et fonctionnelle!
) else (
    echo ATTENTION: API non accessible
)

echo.
echo ========================================
echo   PIPELINE JENKINS SIMULÉ AVEC SUCCÈS
echo   App disponible: http://localhost:8002
echo ========================================