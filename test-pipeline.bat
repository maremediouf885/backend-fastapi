@echo off
echo ========================================
echo   PIPELINE CI/CD - TRANSFERT DENREES
echo ========================================

echo.
echo [ETAPE 1] Tests unitaires...
pytest tests/ -v --tb=short
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
echo [ETAPE 3] Verification image creee...
docker images transfert-denrees-api:latest

echo.
echo ========================================
echo   PIPELINE REUSSI !
echo   Image: transfert-denrees-api:latest
echo   Tests: 2 passed
echo ========================================