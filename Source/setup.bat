@echo off
REM ============================================================
REM PrimaryTeachingSMA - Script d'installation automatique
REM Windows PowerShell / CMD
REM ============================================================

echo ============================================================
echo   INSTALLATION - PrimaryTeachingSMA
echo ============================================================
echo.

REM Vérifier Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Python non installé. Installer Python 3.11 depuis python.org
    pause
    exit /b 1
)
echo [OK] Python détecté

REM Créer environnement virtuel
echo [INFO] Création de l'environnement virtuel...
python -m venv venv
IF %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Impossible de créer le venv
    pause
    exit /b 1
)
echo [OK] Environnement virtuel créé

REM Activer le venv
echo [INFO] Activation du venv...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Mise à jour pip...
python -m pip install --upgrade pip --quiet

REM Installer les dépendances
echo [INFO] Installation des dépendances (peut prendre 3-5 minutes)...
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Erreur lors de l'installation des dépendances
    pause
    exit /b 1
)
echo [OK] Dépendances installées

REM Copier .env.example vers .env si non existant
IF NOT EXIST .env (
    copy .env.example .env
    echo [INFO] Fichier .env créé depuis .env.example
    echo [ACTION REQUISE] Ouvrez .env et ajoutez votre ANTHROPIC_API_KEY
) ELSE (
    echo [OK] Fichier .env déjà présent
)

REM Créer les dossiers outputs et data si nécessaire
IF NOT EXIST outputs mkdir outputs
IF NOT EXIST data mkdir data

echo.
echo ============================================================
echo   INSTALLATION TERMINÉE
echo ============================================================
echo.
echo Prochaines étapes :
echo   1. Editez .env et ajoutez votre ANTHROPIC_API_KEY
echo   2. Testez : python test_api.py
echo   3. Lancez : streamlit run app.py
echo.
pause
