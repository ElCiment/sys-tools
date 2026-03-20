# Outils - Système KPI Tech

Interface d'administration Windows — dark mode — nécessite les droits administrateur.

**Mot de passe :** `Log1tech` ou `Axios1694`
**Lancement :** `python main.py` ou double-clic sur `Sys-Tools.exe`

---

## En-tête (toujours visible)

| Élément | Ce que ça fait | Commande/mécanisme |
|---|---|---|
| Numéro de version | Affiche la version locale | Lit `version.txt` |
| Bouton Mise à jour | Vérifie si une MAJ existe, télécharge et relance l'exe | Compare `version.txt` local à `VERSION_URL` dans `update_config.txt` |
| Password Veloce du jour | Calcule le mot de passe journalier Veloce | Dernier chiffre de jour/mois/année → mapping chiffres→lettres (0=A…9=J) assemblés en `(J)V(M)E(A)L` |
| TeamViewer ID / AnyDesk ID | Récupère et affiche les IDs au démarrage | Interroge les processus locaux TeamViewer/AnyDesk |
| Bouton Clear | Vide la console | — |

---

## Menus (barre du haut)

### Fichier
- Quitter

### Outils — raccourcis Windows natifs
- Panneau de configuration
- Gérer l'ordinateur
- Gestionnaire des tâches
- Programmes et fonctionnalités
- Windows Update
- Connexions réseau

### Système — raccourcis Windows natifs
- Explorateur, msinfo32, PowerShell, regedit, services.msc, msconfig, dossier Démarrage
- **Tweak ChrisTitus**
  - Crée un fichier `.ps1` temporaire dans `%TEMP%` contenant :
    ```
    Set-ExecutionPolicy Bypass -Scope Process -Force
    irm https://christitus.com/win | iex
    ```
  - Lance via `ShellExecuteW(None, "runas", "powershell.exe", "-NoProfile -ExecutionPolicy Bypass -File [ps1]")` (demande UAC)

### Aide
- Release Notes : contenu distant affiché dans une fenêtre
- Téléchargements : ouvre `kpi-tech.ca/launcher/telechargements.html`

---

## Section Setup (menu gauche)

### Auto Setup

#### 🖥️ Config PC — Poste Standard

Fenêtre de progression avec étapes à cocher. S'exécutent dans l'ordre.

| Étape | Commandes exactes |
|---|---|
| Tweak barre des tâches | Registre HKCU :<br>`Explorer\EnableAutoTray = 0`<br>`Policies\Explorer\DisableNotificationCenter = 1`<br>`PushNotifications\ToastEnabled = 0`<br>`Search\SearchboxTaskbarMode = 0`<br>`Explorer\Advanced\ShowTaskViewButton = 0`<br>`Explorer\Advanced\TaskbarGlomLevel = 2`<br>Win11 : `TaskbarAl = 0`, `TaskbarDa = 0`<br>Win10 : `Feeds\ShellFeedsTaskbarViewMode = 2`<br>PowerShell : supprime les raccourcis épinglés sauf Explorateur/Edge |
| Désactiver notifications | Registre HKCU :<br>`PushNotifications\ToastEnabled = 0`<br>`ContentDeliveryManager\SubscribedContent-310093Enabled = 0`<br>`ContentDeliveryManager\SubscribedContent-338389Enabled = 0`<br>`ContentDeliveryManager\SoftLandingEnabled = 0`<br>`UserProfileEngagement\ScoobeSystemSettingEnabled = 0` |
| Désactiver UAC | Registre HKLM `System\CurrentControlSet\Control\Lsa` :<br>`EnableLUA = 0`<br>`ConsentPromptBehaviorAdmin = 0`<br>`PromptOnSecureDesktop = 0` |
| Créer utilisateur `admin` | `net user "admin" "veloce123" /add`<br>`net user "admin" /active:yes`<br>`net localgroup Administrators "admin" /add`<br>`net localgroup Administrateurs "admin" /add`<br>`wmic useraccount where name="admin" set PasswordExpires=False`<br>`net user "admin" /expires:never`<br>+ `net accounts /lockoutthreshold:0 /lockoutduration:0 /lockoutwindow:0` |
| Créer utilisateur `kpitech` | Mêmes commandes avec `kpitech` / `kpitech123` (sans admin) |
| Auto logon admin | Registre HKLM `SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon` :<br>`AutoAdminLogon = "1"`<br>`DefaultUserName = "admin"`<br>`DefaultPassword = "veloce123"` |
| Renommer le PC | PowerShell : `rename-computer -newname "[NOM]" -force` |
| Installation logiciels | 3 tentatives dans l'ordre :<br>1. `winget install --id=[ID] --silent --accept*`<br>2. `choco install [pkg] -y` (installe Chocolatey si absent)<br>3. Téléchargement direct + installeur silencieux depuis site officiel |
| Configuration VNC | `sc config tvnserver start= auto`<br>`net stop tvnserver`<br>Registre HKLM `SOFTWARE\TightVNC\Server` :<br>`Password = 0x5d,0xd9,0xd3,0x3a,0x0c,0xed,0x17,0xdb` (DES de "Log1tech")<br>`net start tvnserver` |
| Redémarrage automatique | `shutdown /r /t 10` |

---

#### 💳 Station Veloce

**Paramètres demandés :** nom du serveur réseau (ex: `SV`) + numéro de station (ex: `1` → formaté `01`)

| Étape | Commandes exactes |
|---|---|
| Installation Veloce | `ShellExecuteW("runas", "\\[SERVEUR]\veloce\stat[XX]\install\install (WSXX).exe")` |
| Raccourci bureau | PowerShell `WScript.Shell.CreateShortcut("...\station X.lnk")` pointant vers `\\[SERVEUR]\veloce\stat[XX]\Veloce WS Starter.exe` |
| Raccourci Démarrage | PowerShell `WScript.Shell.CreateShortcut` dans `shell:startup` |
| Clé registre réseau | HKLM `SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters\DirectoryCacheLifetime = 0` |
| Nettoyage | `os.remove` du raccourci `Veloce WS Starter.exe` sur le bureau |
| Tweaks optionnels | Mêmes étapes que Config PC selon les cases cochées |

---

### Activer Windows

| Élément | Détail |
|---|---|
| Commande affichée | `irm https://get.activated.win \| iex` (non modifiable) |
| Exécution | PowerShell : `-NoProfile -ExecutionPolicy Bypass -Command "irm https://get.activated.win \| iex"` |

---

### Gérer les Utilisateurs

| Action | Commandes exactes |
|---|---|
| Afficher les utilisateurs | `net user` |
| Créer un utilisateur | `net user "[nom]" "[mdp]" /add`<br>`net user "[nom]" /active:yes`<br>Si admin : `net localgroup Administrators "[nom]" /add` + `net localgroup Administrateurs "[nom]" /add`<br>`wmic useraccount where name="[nom]" set PasswordExpires=False`<br>`net user "[nom]" /expires:never`<br>`net accounts /lockoutthreshold:0 /lockoutduration:0 /lockoutwindow:0` |
| Presets rapides | Remplissent le formulaire : `admin / veloce123` (admin) et `kpitech / Log1tech` (admin) |
| Vérifier auto-login | Lit HKLM `Winlogon\AutoAdminLogon` et `DefaultUserName` |
| Activer auto-login | HKLM `Winlogon` : `AutoAdminLogon = "1"`, `DefaultUserName = "[nom]"`, `DefaultPassword = "[mdp]"` |
| Désactiver auto-login | HKLM `Winlogon` : `AutoAdminLogon = "0"`, supprime `DefaultPassword` |

---

### Adresse IP

| Action | Commandes exactes |
|---|---|
| Détecter les interfaces | `psutil.net_if_addrs()` + `netsh interface ip show config` |
| Passer en DHCP | `netsh interface ipv4 set address name="[X]" source=dhcp`<br>`netsh interface ipv4 set dns name="[X]" source=dhcp` |
| IP statique | `netsh interface ipv4 set address name="[X]" static [IP] [MASQUE] [GW]`<br>(sans GW si vide)<br>`netsh interface ipv4 set dns name="[X]" static [DNS1]`<br>`netsh interface ipv4 add dns name="[X]" [DNS2] index=2` |
| Ouvrir propriétés | `rundll32.exe shell32.dll,Control_RunDLL ncpa.cpl` → propriétés de la carte |

---

## Section Système/Windows (menu gauche)

### Infos Système

| Info | Source |
|---|---|
| Nom PC, OS, version, architecture | `socket.gethostname()`, `platform.system()`, `platform.release()`, `platform.version()` |
| CPU modèle | `wmic cpu get name` |
| CPU cœurs / fréquence / usage | `psutil.cpu_count()`, `psutil.cpu_freq()`, `psutil.cpu_percent(interval=1)` |
| RAM | `psutil.virtual_memory()` |
| Disques | `psutil.disk_partitions()` + `psutil.disk_usage()` |

---

### Renommer le PC

| Élément | Commande |
|---|---|
| Renommage | PowerShell : `rename-computer -newname "[NOM]" -force` |
| Redémarrage proposé | `shutdown /r /t 0` |

---

### Tweaks Windows

| Bouton | Commande exacte |
|---|---|
| Désinstaller KB5064081 | `wusa /uninstall /kb:5064081 /norestart` (fenêtre native Windows) |
| Désinstaller une MAJ | Saisie du numéro KB → `wusa /uninstall /kb:[XXXXX] /norestart` (même comportement) |
| Tweak ChrisTitus | Même mécanisme que le menu Système (ps1 temp + ShellExecuteW runas) |
| Wallpaper | `ctypes.windll.user32.SystemParametersInfoW(20, 0, "[chemin]", 3)` |

---

### Commandes personnalisées (CMD)

| Champ | Usage |
|---|---|
| Hôte distant vide | Exécution locale : `subprocess.run([cmd], shell=True)` |
| Hôte distant renseigné | Via PsExec : `psexec.exe \\[hôte] -u [user] -p [pwd] cmd /c [commande]` |
| Commandes rapides | Remplissent le champ : `systeminfo`, `tasklist`, `shutdown /r /t 0`, `cmd.exe` |

---

## Section Réseau (menu gauche)

### Vérifier port TCP

| Étape | Détail |
|---|---|
| IP publique | `GET https://api.ipify.org?format=json` (fallback : `https://api.my-ip.io/ip`) |
| Test port externe | `GET https://api.portchecker.co/check?host=[ip]&port=[port]` |
| Fallback | `POST https://ports.yougetsignal.com/check-port.php` avec `remoteAddress=[ip]&portNumber=[port]` |

> Teste l'accessibilité du port **depuis internet** (pas en local).

---

### Voir mots de passe WiFi

| Commande | But |
|---|---|
| `netsh wlan show profiles` | Liste tous les profils WiFi enregistrés |
| `netsh wlan show profile name="[X]" key=clear` | Extrait le mot de passe en clair pour chaque profil |

---

## Section Imprimantes (menu gauche)

### Test impression

| Mode | Commande/mécanisme |
|---|---|
| TCP/IP | `socket.create_connection((IP, port))` → envoi bytes ESC/P |
| COM (série) | `serial.Serial(port, baudrate)` → envoi bytes ESC/P (`pyserial`) |
| Couleur rouge | Commande ESC/P : `\x1b\x72\x01` (sélection couleur rouge) |
| Retour noir | Commande ESC/P : `\x1b\x72\x00` |

---

## Fichiers de configuration

| Fichier | Rôle |
|---|---|
| `version.txt` | Version locale (ex: `2.2.3`) — comparée au serveur pour détecter les MAJ |
| `update_config.txt` | `VERSION_URL` et `DOWNLOAD_URL` pour le système de mise à jour |
| `main.py` ligne `PASSWORDS` | Mots de passe acceptés : `["Log1tech", "Axios1694"]` |
| `assets/wallpapers/` | Images `.jpg/.png/.bmp` disponibles dans le sélecteur de fond d'écran |

---

## Lancement et compilation

```bash
# Développement
pip install -r requirements.txt
python main.py

# Compilation exe
pyinstaller --onefile --noconsole --clean \
    --icon=mainicon2.ico \
    --add-data "version.txt;." \
    --add-data "update_config.txt;." \
    --add-data "assets;assets" \
    --hidden-import=customtkinter \
    --hidden-import=PIL \
    --hidden-import=psutil \
    --hidden-import=pyserial \
    --name "Sys-Tools" \
    main.py
```

---

## Structure des fichiers

```
├── main.py                  # Authentification + lancement
├── version.txt
├── update_config.txt
├── assets/
│   └── wallpapers/
├── utils/
│   ├── system_utils.py      # is_admin(), get_base_path(), relaunch_as_admin()
│   └── update_manager.py    # check_for_updates(), download_update()
├── services/
│   ├── printer_service.py   # ESC/P TCP et COM
│   ├── windows_service.py   # Tweaks, registre, utilisateurs
│   └── network_service.py   # Port TCP, WiFi, TeamViewer/AnyDesk
└── ui/
    ├── password_dialog.py
    └── main_window.py       # Toute l'interface (~6000 lignes)
```
