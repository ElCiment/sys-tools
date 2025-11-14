"""
Gestionnaire de mises à jour pour Sys-Tools
Vérifie et télécharge les mises à jour depuis kpi-tech.ca
"""

import urllib.request
import urllib.error
import subprocess
import os
import tempfile
from typing import Tuple, Optional

# URLs des fichiers de mise à jour (lues depuis update_config.txt)
def _load_update_urls():
    """Charge les URLs depuis le fichier update_config.txt"""
    try:
        import os
        # Déterminer le chemin du fichier update_config.txt
        if getattr(subprocess.sys, 'frozen', False):
            # Mode exe compilé - fichiers embedés dans l'exe
            base_path = subprocess.sys._MEIPASS
        else:
            # Mode développement
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        config_file = os.path.join(base_path, "update_config.txt")
        
        # Valeurs par défaut
        version_url = "https://kpi-tech.ca/launcher/files/systools/version.txt"
        download_url = "https://github.com/ElCiment/sys-tools/releases/download/sys-tools/Sys-Tools.exe"
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Ignorer commentaires et lignes vides
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parser VERSION_URL=...
                    if line.startswith('VERSION_URL='):
                        version_url = line.split('=', 1)[1].strip()
                    # Parser DOWNLOAD_URL=...
                    elif line.startswith('DOWNLOAD_URL='):
                        download_url = line.split('=', 1)[1].strip()
        
        return version_url, download_url
    except Exception:
        # En cas d'erreur, utiliser les URLs par défaut
        return ("https://kpi-tech.ca/launcher/files/systools/version.txt",
                "https://github.com/ElCiment/sys-tools/releases/download/sys-tools/Sys-Tools.exe")

VERSION_URL, DOWNLOAD_URL = _load_update_urls()

# Version locale (lue depuis version.txt)
def _get_local_version():
    """Lit le numéro de version depuis version.txt"""
    try:
        import os
        # Déterminer le chemin du fichier version.txt
        if getattr(subprocess.sys, 'frozen', False):
            # Mode exe compilé - fichiers embedés dans l'exe
            base_path = subprocess.sys._MEIPASS
        else:
            # Mode développement
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        version_file = os.path.join(base_path, "version.txt")
        
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        else:
            # Fallback si le fichier n'existe pas
            return "2.1.1"
    except Exception:
        return "2.1.1"

LOCAL_VERSION = _get_local_version()


def get_remote_version() -> Optional[str]:
    """
    Récupère le numéro de version depuis le serveur
    
    Returns:
        str: Numéro de version (ex: "2.1.1") ou None si erreur
    """
    try:
        with urllib.request.urlopen(VERSION_URL, timeout=5) as response:
            version = response.read().decode('utf-8').strip()
            return version
    except Exception as e:
        print(f"Erreur récupération version: {e}")
        return None


def compare_versions(version1: str, version2: str) -> int:
    """
    Compare deux numéros de version (format: x.y.z)
    
    Args:
        version1: Première version
        version2: Deuxième version
    
    Returns:
        -1 si version1 < version2 (mise à jour disponible)
         0 si version1 == version2 (à jour)
         1 si version1 > version2 (version plus récente)
    """
    try:
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        # Égaliser la longueur avec des 0
        while len(v1_parts) < len(v2_parts):
            v1_parts.append(0)
        while len(v2_parts) < len(v1_parts):
            v2_parts.append(0)
        
        for i in range(len(v1_parts)):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1
        
        return 0
    except Exception:
        return 0


def check_for_updates() -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Vérifie si une mise à jour est disponible
    
    Returns:
        Tuple: (update_available, local_version, remote_version)
    """
    remote_version = get_remote_version()
    
    if not remote_version:
        return False, LOCAL_VERSION, None
    
    comparison = compare_versions(LOCAL_VERSION, remote_version)
    update_available = comparison < 0
    
    return update_available, LOCAL_VERSION, remote_version




def download_update(progress_callback=None) -> Optional[str]:
    """
    Télécharge la mise à jour depuis le serveur plus rapidement
    """
    try:
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "Sys-Tools-Update.exe")
        
        with urllib.request.urlopen(DOWNLOAD_URL) as response:
            total_size = int(response.getheader('Content-Length', 0))
            downloaded = 0
            chunk_size = 1024 * 1024 * 5  # 5 Mo par chunk pour accélérer

            with open(temp_file, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total_size > 0:
                        progress_callback(downloaded, total_size)

        return temp_file
    except Exception as e:
        print(f"Erreur téléchargement: {e}")
        return None


def install_update(update_file: str) -> bool:
    """
    Lance l'installation de la mise à jour et ferme l'application actuelle
    """
    try:
        current_exe = os.path.abspath(subprocess.sys.executable)
        exe_name = os.path.basename(current_exe)
        exe_dir = os.path.dirname(current_exe)

        if getattr(subprocess.sys, 'frozen', False):
            batch_script = f"""@echo off
echo Mise a jour en cours...
start "" "{update_file}"
timeout /t 5 /nobreak >nul
taskkill /F /IM "{exe_name}" >nul 2>&1
:waitloop
tasklist /FI "IMAGENAME eq {exe_name}" 2>NUL | find /I "{exe_name}" >nul
if "%ERRORLEVEL%"=="0" (
    timeout /t 1 /nobreak >nul
    goto waitloop
)
copy /Y "{update_file}" "{current_exe}" >nul
del "{update_file}" >nul 2>&1
"""

            batch_file = os.path.join(tempfile.gettempdir(), "update_systools.bat")
            with open(batch_file, 'w') as f:
                f.write(batch_script)

            # Lancer le batch et quitter l'application actuelle
            subprocess.Popen(batch_file, shell=True)
            return True
        else:
            # Mode dev
            os.startfile(update_file)
            return True

    except Exception as e:
        print(f"Erreur installation: {e}")
        return False