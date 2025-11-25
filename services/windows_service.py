"""
Service de gestion Windows
Gère les tweaks système, le registre, les utilisateurs et les KB Windows
"""
import subprocess
import os
import winreg
from utils.system_utils import is_admin, relaunch_as_admin


def tweak_taskbar(log_fn):
    """
    Applique des tweaks complets à la barre des tâches Windows 10 & 11
    - Affiche tous les icônes de la barre d'état système
    - Désactive Action Center, Search, Task View, News/Widgets
    - Affiche l'icône du clavier tactile
    - Nettoie les icônes épinglés (garde seulement Explorateur & Edge)
    - Win11: Aligne les icônes à gauche
    
    Args:
        log_fn (callable): Fonction de logging
    """
    if not is_admin():
        log_fn("🔼 Nécessite les droits administrateur")
        try:
            relaunch_as_admin()
        except Exception as e:
            log_fn(f"❌ Impossible de relancer en admin: {e}")
        return
    
    log_fn("▶ Application des tweaks de la barre des tâches...")
    
    # Détecter Windows 10 ou 11 via build number
    try:
        import sys
        build = sys.getwindowsversion().build
        is_win11 = build >= 22000
        version_name = "11" if is_win11 else "10"
        log_fn(f"  Détecté: Windows {version_name} (build {build})")
    except:
        is_win11 = False
        log_fn("  Détection version échouée, assume Windows 10")
    
    tweaks = [
        # === COMMUN Windows 10 & 11 ===
        # Afficher tous les icônes dans la barre d'état système (System Tray)
        (r"Software\Microsoft\Windows\CurrentVersion\Explorer", "EnableAutoTray", 0),
        
        # Désactiver Action Center
        (r"Software\Policies\Microsoft\Windows\Explorer", "DisableNotificationCenter", 1),
        (r"Software\Microsoft\Windows\CurrentVersion\PushNotifications", "ToastEnabled", 0),
        
        # Désactiver l'icône de recherche (Windows 10)
        (r"Software\Microsoft\Windows\CurrentVersion\Search", "SearchboxTaskbarMode", 0),
        
        # Désactiver l'icône de vue des tâches (Task View)
        (r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowTaskViewButton", 0),
        
        # Afficher l'icône du clavier tactile
        (r"Software\Microsoft\TabletTip\1.7", "TipbandDesiredVisibility", 1),
        
        # Petites icônes + ne pas combiner les boutons
        #(r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarSmallIcons", 1),
        (r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarGlomLevel", 2),
    ]
    
    # === TWEAKS SPÉCIFIQUES Windows 11 ===
    if is_win11:
        log_fn("  → Tweaks spécifiques Windows 11...")
        tweaks.extend([
            # Aligner les icônes à gauche
            (r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarAl", 0),
            
            # Désactiver les widgets
            (r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarDa", 0),
        ])
    else:
        log_fn("  → Tweaks spécifiques Windows 10...")
        # Désactiver les actualités et centres d'intérêts (Windows 10)
        tweaks.append((r"Software\Microsoft\Windows\CurrentVersion\Feeds", "ShellFeedsTaskbarViewMode", 2))
    
    # Appliquer les tweaks de registre
    try:
        for key_path, value_name, value_data in tweaks:
            try:
                # Créer la clé si elle n'existe pas
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                except FileNotFoundError:
                    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                
                winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
                winreg.CloseKey(key)
                log_fn(f"  ✓ {value_name} = {value_data}")
            except Exception as e:
                log_fn(f"  ⚠️ Erreur pour {value_name}: {e}")
        
        # Nettoyer les icônes épinglés (garder seulement Explorateur & Edge)
        log_fn("  → Nettoyage des icônes épinglés...")
        try:
            # Commande PowerShell pour supprimer les épinglés sauf Explorateur et Edge
            ps_cmd = """
            $pinnedPath = "$env:APPDATA\\Microsoft\\Internet Explorer\\Quick Launch\\User Pinned\\TaskBar"
            if (Test-Path $pinnedPath) {
                Get-ChildItem $pinnedPath | Where-Object {
                    $_.Name -notmatch 'explorer|edge|file explorer'
                } | Remove-Item -Force -ErrorAction SilentlyContinue
            }
            """
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
            log_fn("  ✓ Icônes épinglés nettoyés (gardé Explorateur & Edge)")
        except Exception as e:
            log_fn(f"  ⚠️ Nettoyage épinglés échoué: {e}")
        
        log_fn("✅ Tweaks de la barre des tâches appliqués")
        log_fn("⚠️ Redémarrez Explorer (Ctrl+Shift+Esc → Explorer.exe → Redémarrer)")
        log_fn("   ou redémarrez le PC pour voir tous les changements")
        
    except Exception as e:
        log_fn(f"❌ Erreur globale: {e}")


def restore_context_menu(log_fn):
    """
    Rétablit le menu contextuel classique de Windows 11
    
    Args:
        log_fn (callable): Fonction de logging
    """
    if not is_admin():
        log_fn("🔼 Nécessite les droits administrateur")
        try:
            relaunch_as_admin()
        except Exception as e:
            log_fn(f"❌ Impossible de relancer en admin: {e}")
        return
    
    # Commande corrigée : ajouter une clé vide pour forcer le menu classique
    reg_cmd = r'reg.exe add "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /f /ve'
    log_fn("▶ Restauration du menu contextuel classique...")
    
    try:
        result = subprocess.run(reg_cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            log_fn("✅ Menu contextuel classique restauré")
            log_fn("⚠️ Redémarrez Explorer (Ctrl+Shift+Esc → Explorer.exe → Redémarrer)")
            log_fn("   ou redémarrez le PC pour appliquer")
        else:
            log_fn(f"⚠️ Code retour: {result.returncode}")
            if result.stderr:
                log_fn(result.stderr)
    except Exception as e:
        log_fn(f"❌ Erreur: {e}")


def uninstall_kb5064081(log_fn):
    """
    Désinstalle la mise à jour KB5064081
    
    Args:
        log_fn (callable): Fonction de logging
    """
    if not is_admin():
        log_fn("🔼 Nécessite les droits administrateur")
        try:
            relaunch_as_admin()
        except Exception as e:
            log_fn(f"❌ Impossible de relancer en admin: {e}")
        return
    
    cmd = "wusa /uninstall /kb:5064081 /norestart"
    log_fn("▶ Désinstallation de KB5064081...")
    
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        
        if proc.stdout:
            log_fn("----- Sortie wusa -----")
            for ln in proc.stdout.splitlines():
                log_fn(ln)
        
        if proc.stderr:
            log_fn("----- Erreurs wusa -----")
            for ln in proc.stderr.splitlines():
                log_fn(ln)
        
        log_fn(f"wusa terminé (code {proc.returncode})")
        
    except subprocess.TimeoutExpired:
        log_fn("❌ wusa: timeout après 5 minutes")
    except Exception as e:
        log_fn(f"❌ Erreur d'exécution: {e}")


def disable_windows_notifications(log_fn):
    """
    Désactive toutes les notifications Windows (toast + suggestions + conseils)
    
    Args:
        log_fn (callable): Fonction de logging
    """
    log_fn("▶ Désactivation des notifications Windows...")
    
    try:
        # 1. Désactiver les notifications toast
        key_path = r"Software\Microsoft\Windows\CurrentVersion\PushNotifications"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "ToastEnabled", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        log_fn("  ✓ Notifications toast désactivées")
        
        # 2. Désactiver "Afficher l'expérience de bienvenue" + "Obtenez des conseils..."
        key_path = r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        except:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        
        winreg.SetValueEx(key, "SubscribedContent-310093Enabled", 0, winreg.REG_DWORD, 0)  # Bienvenue
        winreg.SetValueEx(key, "SubscribedContent-338389Enabled", 0, winreg.REG_DWORD, 0)  # Conseils
        winreg.SetValueEx(key, "SoftLandingEnabled", 0, winreg.REG_DWORD, 0)  # Suggestions
        winreg.CloseKey(key)
        log_fn("  ✓ Expérience de bienvenue désactivée")
        log_fn("  ✓ Conseils et astuces désactivés")
        
        # 3. Désactiver "Suggest ways I can finish setting up..."
        key_path = r"Software\Microsoft\Windows\CurrentVersion\UserProfileEngagement"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        except:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        
        winreg.SetValueEx(key, "ScoobeSystemSettingEnabled", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        log_fn("  ✓ Suggestions de configuration désactivées")
        
        log_fn("✅ Toutes les notifications désactivées")
    except Exception as e:
        log_fn(f"❌ Erreur: {e}")


def apply_wallpaper(wallpaper_file, log_fn):
    """
    Applique un fond d'écran
    
    Args:
        wallpaper_file (str): Nom du fichier wallpaper
        log_fn (callable): Fonction de logging
    """
    from utils.system_utils import get_resource_path
    
    try:
        wallpaper_path = get_resource_path(wallpaper_file)
        
        if not os.path.exists(wallpaper_path):
            log_fn(f"❌ Fichier introuvable: {wallpaper_path}")
            return
        
        import ctypes
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, wallpaper_path, 3)
        log_fn(f"✅ Fond d'écran appliqué: {wallpaper_file}")
    except Exception as e:
        log_fn(f"❌ Erreur lors de l'application du wallpaper: {e}")


def rename_computer(new_name, log_fn):
    """
    Renomme l'ordinateur
    
    Args:
        new_name (str): Nouveau nom
        log_fn (callable): Fonction de logging
    
    Returns:
        bool: True si renommage réussi
    """
    if not new_name:
        log_fn("⚠️ Aucun nom saisi")
        return False
    
    if not is_admin():
        log_fn("🔼 Nécessite les droits administrateur")
        try:
            relaunch_as_admin()
        except Exception as e:
            log_fn(f"❌ Impossible de relancer en admin: {e}")
        return False
    
    cmd = f'rename-computer -newname "{new_name}" -force'
    log_fn(f"▶ Renommage du PC: {new_name}")
    
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd],
            check=True, capture_output=True, text=True
        )
        log_fn(f"✅ PC renommé en '{new_name}'. Redémarrage recommandé.")
        return True
    except subprocess.CalledProcessError as e:
        log_fn(f"❌ Erreur lors du renommage: {e.stderr}")
        return False
    except Exception as e:
        log_fn(f"❌ Exception: {e}")
        return False


def add_windows_user(username, password, make_admin, password_never_expires, log_fn):
    """
    Ajoute un utilisateur Windows
    
    Args:
        username (str): Nom d'utilisateur
        password (str): Mot de passe
        make_admin (bool): Ajouter aux administrateurs
        password_never_expires (bool): Mot de passe n'expire jamais
        log_fn (callable): Fonction de logging
    """
    if not username or not password:
        log_fn("❌ Nom d'utilisateur ou mot de passe vide")
        return
    
    if not is_admin():
        log_fn("🔼 Nécessite les droits administrateur")
        try:
            relaunch_as_admin()
        except Exception as e:
            log_fn(f"❌ Impossible de relancer en admin: {e}")
        return
    
    cmds = [
        f'net user "{username}" "{password}" /add',
        f'net user "{username}" /active:yes',
    ]
    
    if make_admin:
        cmds.append(f'net localgroup Administrators "{username}" /add')
        cmds.append(f'net localgroup Administrateurs "{username}" /add')
    
    if password_never_expires:
        cmds.append(f'wmic useraccount where name="{username}" set PasswordExpires=False')
        cmds.append(f'net user "{username}" /expires:never')
    
    for cmd in cmds:
        log_fn(f"Exécution: {cmd}")
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                log_fn("✅ Commande exécutée")
            else:
                log_fn(f"⚠️ Code retour: {res.returncode}")
                if res.stderr:
                    log_fn(res.stderr)
        except Exception as e:
            log_fn(f"❌ Erreur: {e}")
    
    log_fn(f"✅ Utilisateur '{username}' créé")
    
    
    # ---- Ajout AUTOMATIQUE : appliquer le verrouillage de compte ----
    lock_cmds = [
        'net accounts /lockoutthreshold:0',
        'net accounts /lockoutduration:0',
        'net accounts /lockoutwindow:0'
    ]

    log_fn("🔧 Application des paramètres de verrouillage de compte…")
    for cmd in lock_cmds:
        log_fn(f"Exécution: {cmd}")
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                log_fn("   → OK")
            else:
                log_fn(f"   ⚠ Code retour: {res.returncode}")
                if res.stderr:
                    log_fn(f"   {res.stderr}")
        except Exception as e:
            log_fn(f"❌ Erreur: {e}")
    
    log_fn(f"✅ Utilisateur '{username}' créé (avec verrouillage appliqué)")
    
    


def create_veloce_shortcuts(folder, log_fn):
    """
    Crée les raccourcis VELBO et VELSRV sur le bureau
    
    Args:
        folder (str): Dossier contenant velbo.exe et velsrv.exe
        log_fn (callable): Fonction de logging
    """
    if not folder or not os.path.isdir(folder):
        log_fn("❌ Le dossier indiqué n'existe pas")
        return
    
    log_fn("▶ Création des raccourcis VELBO/VELSRV...")
    
    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        
        ps_script = f'''
        [System.Threading.Thread]::CurrentThread.ApartmentState = [System.Threading.ApartmentState]::STA
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{os.path.join(desktop, "VELBO.lnk")}")
        $Shortcut.TargetPath = "{os.path.join(folder, "velbo.exe")}"
        $Shortcut.WorkingDirectory = "{folder}"
        $Shortcut.Save()
        
        $Shortcut2 = $WshShell.CreateShortcut("{os.path.join(desktop, "VELSRV.lnk")}")
        $Shortcut2.TargetPath = "{os.path.join(folder, "velsrv.exe")}"
        $Shortcut2.WorkingDirectory = "{folder}"
        $Shortcut2.IconLocation = "{os.path.join(folder, "velsrv.exe")},1"
        $Shortcut2.Save()
        '''
        
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True, text=True, check=True
        )
        
        log_fn("✅ Raccourcis créés avec succès")
        log_fn("✅ VELBO.lnk sur le Bureau")
        log_fn("✅ VELSRV.lnk sur le Bureau")
        
    except subprocess.CalledProcessError as e:
        log_fn(f"❌ Erreur PowerShell: {e.stderr}")
    except Exception as e:
        log_fn(f"❌ Erreur création raccourcis: {e}")


def apply_wallpaper(wallpaper_filename, log_fn):
    """
    Applique le wallpaper sélectionné
    
    Args:
        wallpaper_filename (str): Nom du fichier wallpaper
        log_fn (callable): Fonction de logging
    """
    import ctypes
    import sys
    import os
    
    # Déterminer le chemin de base
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(__file__))
    
    wallpaper_path = os.path.join(base_path, "assets", "wallpapers", wallpaper_filename)
    
    if not os.path.exists(wallpaper_path):
        log_fn(f"❌ Fichier {wallpaper_filename} introuvable dans assets/wallpapers/")
        return
    
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 3)
        log_fn(f"✅ Wallpaper '{wallpaper_filename}' appliqué avec succès")
    except Exception as e:
        log_fn(f"❌ Erreur lors de l'application du wallpaper: {e}")


def restore_context_menu_win11(log_fn):
    """
    Rétablit le menu contextuel Windows 10 sur Windows 11
    
    Args:
        log_fn (callable): Fonction de logging
    """
    cmd = [
        "reg.exe", "add",
        r'HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32',
        "/f", "/ve"
    ]
    
    log_fn(f"Exécution: {' '.join(cmd)}")
    
    def worker():
        try:
            res = subprocess.run(cmd, check=False, capture_output=True, text=True)
            if res.returncode == 0:
                log_fn("✅ Clé de registre ajoutée avec succès")
                if res.stdout.strip():
                    log_fn(res.stdout.strip())
            else:
                log_fn(f"❌ reg.exe a renvoyé code {res.returncode}")
                if res.stdout.strip():
                    log_fn(res.stdout.strip())
                if res.stderr.strip():
                    log_fn(res.stderr.strip())
        except Exception as e:
            log_fn(f"❌ Erreur lors de l'exécution de reg.exe: {e}")
    
    threading.Thread(target=worker, daemon=True).start()
