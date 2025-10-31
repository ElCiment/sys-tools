"""
Utilitaires système pour Windows
Gère l'élévation des privilèges, la détection de la plateforme et les ressources PyInstaller
"""
import sys
import os
import ctypes


def is_windows():
    """Vérifie si le système d'exploitation est Windows"""
    return sys.platform.startswith("win")


def is_admin():
    """
    Vérifie si le script est exécuté avec les privilèges administrateur
    Returns:
        bool: True si administrateur, False sinon
    """
    if not is_windows():
        return False
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def relaunch_as_admin():
    """
    Relance le script Python en mode administrateur (Windows uniquement)
    Raises:
        RuntimeError: Si appelé sur un système non-Windows
    """
    if not is_windows():
        raise RuntimeError("Élévation d'admin uniquement sous Windows.")
    
    executable = sys.executable
    params = " ".join(f'"{arg}"' for arg in sys.argv) + ' --skip-password'
    
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", executable, params, None, 1
        )
        return True
    except Exception as e:
        raise RuntimeError(f"Impossible de relancer en admin: {e}")


def run_elevated_program(exe, args):
    """
    Lance un exécutable avec élévation de privilèges (UAC)
    
    Args:
        exe (str): Chemin vers l'exécutable
        args (str): Arguments de ligne de commande
    
    Returns:
        bool: True si lancé avec succès, False sinon
    """
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, args, None, 1)
        return True
    except Exception:
        return False


def get_resource_path(filename):
    """
    Retourne le chemin correct vers un fichier inclus avec PyInstaller
    
    Args:
        filename (str): Nom du fichier
    
    Returns:
        str: Chemin complet vers le fichier
    """
    if getattr(sys, "frozen", False):
        # PyInstaller crée un dossier temporaire pour les fichiers ajoutés
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(__file__))
    
    return os.path.join(base_path, filename)


def get_base_path():
    """
    Retourne le chemin de base du projet
    
    Returns:
        str: Chemin de base
    """
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
