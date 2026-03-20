@echo off
setlocal enabledelayedexpansion

:: --- Configuration des dossiers ---
:: On part du principe que le script est à la racine de votre projet
set "ICON_DIR=assets\icons"
set "IMG_DIR=assets\images"

echo [+] Debut du renommage des assets...

:: --- Traitement des ICONES ---
if exist "%ICON_DIR%" (
    pushd "%ICON_DIR%"
    if exist "mainicon.ico" rename "mainicon.ico" "axios.ico"
    if exist "kpi.ico" rename "kpi.ico" "mainicon.ico"
    popd
    echo [OK] Icones traitees.
) else (
    echo [ERREUR] Dossier %ICON_DIR% introuvable.
)

:: --- Traitement des IMAGES ---
if exist "%IMG_DIR%" (
    pushd "%IMG_DIR%"
    if exist "mainlogo.png" rename "mainlogo.png" "axios.png"
    if exist "kpi.png" rename "kpi.png" "mainlogo.png"
    popd
    echo [OK] Images traitees.
) else (
    echo [ERREUR] Dossier %IMG_DIR% introuvable.
)

echo.
echo Operation terminee avec succes !


pyinstaller --onefile --noconsole --clean --icon=mainicon2.ico --add-data "config/psexec.exe;config" --add-data "version.txt;." --add-data "update_config.txt;." --add-data "mainicon.ico;." --add-data "mainicon2.ico;." --add-data "assets;assets" --hidden-import=customtkinter --hidden-import=PIL --hidden-import=psutil --hidden-import=pyserial --name "Sys-Tools" main.py
pause