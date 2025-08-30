@echo off
echo ========================================
echo   PIPELINE CI/CD - TRANSFERT DENREES
echo ========================================

echo.
echo [ETAPE 1] Tests unitaires...
pytest tests/ -v
if %errorlevel% neq 0 (
    echo ECHEC: Tests unitaires
    exit /b 1
)

echo.
echo [ETAPE 2] Construction image Docker...
docker build -t transfert-denrees-api:latest .
if %errorlevel% neq 0 (
    echo ECHEC: Construction Docker
    exit /b 1
)

echo.
echo [ETAPE 3] Test de l'image...
docker run -d --name test-api -p 8001:8000 transfert-denrees-api:latest
timeout /t 5
curl -f http://localhost:8001/status
set curl_result=%errorlevel%
docker stop test-api
docker rm test-api

if %curl_result% neq 0 (
    echo ECHEC: Test de l'API
    exit /b 1
)

echo.
echo ========================================
echo   PIPELINE REUSSI !
echo ========================================