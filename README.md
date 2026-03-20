# Outils - Système KPI Tech

Interface d'administration Windows — dark mode — nécessite les droits administrateur.


**Lancement :** `python main.py` ou double-clic sur `Sys-Tools.exe`

---

## En-tête (toujours visible)

| Élément | Ce que ça fait | Commande / mécanisme |
|---|---|---|
| Numéro de version | Affiche la version locale | Lit `version.txt` |
| Bouton Mise à jour | Vérifie si une MAJ existe, télécharge et relance l'exe | Compare `version.txt` local à `VERSION_URL` dans `update_config.txt` |
| Password Veloce du jour | Calcule le mot de passe journalier Veloce | Dernier chiffre de jour/mois/année → mapping 0=A…9=J → assemblés en `(J)V(M)E(A)L` |
| TeamViewer ID / AnyDesk ID | Récupère et affiche les IDs au démarrage | Interroge les processus locaux TeamViewer / AnyDesk |
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
- **Tweak ChrisTitus** — crée un `.ps1` dans `%TEMP%` puis lance via `ShellExecuteW runas` (demande UAC) :
  ```
  Set-ExecutionPolicy Bypass -Scope Process -Force
  irm https://christitus.com/win | iex
  ```

### Aide
- Release Notes : contenu distant affiché dans une fenêtre
- Téléchargements : ouvre `kpi-tech.ca/launcher/telechargements.html`

---

## Section Setup (menu gauche)

### Auto Setup

---

#### 🖥️ Config PC — Poste Standard

Fenêtre de progression avec étapes à cocher. S'exécutent dans l'ordre.

| Étape | Commandes exactes |
|---|---|
| Tweak barre des tâches | Registre **HKCU** :<br>`Explorer\EnableAutoTray = 0`<br>`Policies\Explorer\DisableNotificationCenter = 1`<br>`PushNotifications\ToastEnabled = 0`<br>`Search\SearchboxTaskbarMode = 0`<br>`Explorer\Advanced\ShowTaskViewButton = 0`<br>`Explorer\Advanced\TaskbarGlomLevel = 2`<br>Win11 : `TaskbarAl = 0`, `TaskbarDa = 0`<br>Win10 : `Feeds\ShellFeedsTaskbarViewMode = 2`<br>PowerShell : supprime les raccourcis épinglés sauf Explorateur/Edge |
| Désactiver notifications | Registre **HKCU** :<br>`PushNotifications\ToastEnabled = 0`<br>`ContentDeliveryManager\SubscribedContent-310093Enabled = 0`<br>`ContentDeliveryManager\SubscribedContent-338389Enabled = 0`<br>`ContentDeliveryManager\SoftLandingEnabled = 0`<br>`UserProfileEngagement\ScoobeSystemSettingEnabled = 0` |
| User 'admin' | `net user "admin" "veloce123" /add`<br>`net user "admin" /active:yes`<br>`net localgroup Administrators "admin" /add`<br>`net localgroup Administrateurs "admin" /add`<br>`wmic useraccount where name="admin" set PasswordExpires=False`<br>`net user "admin" /expires:never`<br>`net accounts /lockoutthreshold:0 /lockoutduration:0 /lockoutwindow:0` |
| User 'kpitech' | Mêmes commandes avec `kpitech` / `Log1tech` (admin) |
| Auto logon admin | Registre **HKLM** `Winlogon` :<br>`AutoAdminLogon = "1"`, `DefaultUserName = "admin"`, `DefaultPassword = "veloce123"` |
| Wallpaper KPI | `ctypes.windll.user32.SystemParametersInfoW(20, 0, "[chemin assets/wallpapers/]", 3)` |
| Désactiver UAC | Registre **HKLM** `System\CurrentControlSet\Control\Lsa` :<br>`EnableLUA = 0`<br>`ConsentPromptBehaviorAdmin = 0`<br>`PromptOnSecureDesktop = 0` |
| Désact. veille réseau | PowerShell : `Get-NetAdapter \| ForEach-Object { MSPower_DeviceEnable.Enable = $false }` (désactive "Autoriser l'ordi à éteindre ce périphérique" pour chaque carte)<br>Fallback : `powercfg /change standby-timeout-ac 0` + `standby-timeout-dc 0` |
| Réseau mode Privé | PowerShell : `Get-NetConnectionProfile \| Set-NetConnectionProfile -NetworkCategory Private` |
| Fuseau horaire + sync | `tzutil /s "Eastern Standard Time"`<br>`net stop w32time`<br>`sc config w32time start= auto`<br>`net start w32time`<br>`w32tm /register`<br>`w32tm /config /manualpeerlist:"time.windows.com,time.nist.gov,pool.ntp.org" /syncfromflags:manual /reliable:YES /update`<br>`w32tm /resync /force` |
| Meilleures perfs | Registre **HKCU** :<br>`Explorer\VisualEffects\VisualFXSetting = 2`<br>`Control Panel\Desktop\WindowMetrics\MinAnimate = "0"` |
| Alimentation perf. | `powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c` (profil Performance élevée)<br>`powercfg /change standby-timeout-ac 0` + `dc 0`<br>`powercfg /change monitor-timeout-ac 0` + `dc 0`<br>`powercfg /change disk-timeout-ac 0` + `dc 0`<br>Registre : Bouton Power → Arrêter, Bouton Veille → Veille, Fermeture capot → Veille |
| Modifier heures actives | Registre **HKLM** `SOFTWARE\Microsoft\WindowsUpdate\UX\Settings` :<br>`ActiveHoursStart = [heure début]` (défaut 8)<br>`ActiveHoursEnd = [heure fin]` (défaut 17)<br>Windows ne redémarre pas automatiquement pendant ces heures |
| Rétablir menu contextuel classique (Win11) | `reg.exe add "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /f /ve` |
| Modifier protection partage réseau | **Désactiver protection** (accès sans mot de passe) :<br>`HKLM\Lsa\everyoneincludesanonymous = 1`<br>`LanmanServer\Parameters\RestrictNullSessAccess = 0`<br>`Lsa\ForceGuest = 0`<br>`Policies\System\LocalAccountTokenFilterPolicy = 1`<br>**Activer protection** : mêmes clés, valeurs inversées |
| Installation logiciels | 3 tentatives dans l'ordre :<br>1. `winget install --id=[ID] --silent --accept*`<br>2. `choco install [pkg] -y` (installe Chocolatey si absent)<br>3. Téléchargement direct + installeur silencieux depuis site officiel |
| Configuration VNC | `sc config tvnserver start= auto`<br>`net stop tvnserver`<br>Registre **HKLM** `SOFTWARE\TightVNC\Server` :<br>`Password = 0x5d,0xd9,0xd3,0x3a,0x0c,0xed,0x17,0xdb` (DES de "Log1tech")<br>`net start tvnserver` |
| Renommer le PC | PowerShell : `rename-computer -newname "[NOM]" -force` |
| Redémarrage automatique | `shutdown /r /t 10` |

---

#### 🖥️ Config PC — Poste Serveur

| Étape | Commandes exactes |
|---|---|
| Raccourcis Bureau VELBO/VELSRV | PowerShell `WScript.Shell.CreateShortcut` → `VELBO.lnk` et `VELSRV.lnk` sur le bureau pointant vers `velbo.exe` / `velsrv.exe` dans le dossier sélectionné |
| Veloce dans pare-feu | `netsh advfirewall firewall add rule name="Veloce Backoffice" dir=in action=allow program="C:\Veloce\VelSrv\VelSrv.exe" enable=yes profile=any`<br>Si règle existe déjà : `netsh advfirewall firewall set rule name="Veloce Backoffice" new enable=yes profile=any` |
| Partager c:\veloce (Everyone - Contrôle total) | `net share veloce /delete` (supprime l'ancien partage)<br>`net share veloce=C:\veloce /grant:everyone,full` |

---

#### 💳 Station Veloce

**Paramètres demandés :** nom du serveur réseau (ex: `SV`) + numéro de station (ex: `1` → formaté `01`)

| Étape | Commandes exactes |
|---|---|
| Installation Veloce | `ShellExecuteW("runas", "\\[SERVEUR]\veloce\stat[XX]\install\install (WSXX).exe")` |
| Raccourci bureau | PowerShell `WScript.Shell.CreateShortcut("...\station X.lnk")` → `\\[SERVEUR]\veloce\stat[XX]\Veloce WS Starter.exe` |
| Raccourci Démarrage | PowerShell `WScript.Shell.CreateShortcut` dans `shell:startup` |
| Clé registre réseau | `HKLM\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters\DirectoryCacheLifetime = 0` |
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
| Vérifier auto-login | Lit **HKLM** `Winlogon\AutoAdminLogon` et `DefaultUserName` |
| Activer auto-login | **HKLM** `Winlogon` : `AutoAdminLogon = "1"`, `DefaultUserName = "[nom]"`, `DefaultPassword = "[mdp]"` |
| Désactiver auto-login | **HKLM** `Winlogon` : `AutoAdminLogon = "0"`, supprime `DefaultPassword` |

---

### Adresse IP

| Action | Commandes exactes |
|---|---|
| Détecter les interfaces | `psutil.net_if_addrs()` + `netsh interface ip show config` |
| Passer en DHCP | `netsh interface ipv4 set address name="[X]" source=dhcp`<br>`netsh interface ipv4 set dns name="[X]" source=dhcp` |
| IP statique | `netsh interface ipv4 set address name="[X]" static [IP] [MASQUE] [GW]`<br>(sans GW si vide)<br>`netsh interface ipv4 set dns name="[X]" static [DNS1]`<br>`netsh interface ipv4 add dns name="[X]" [DNS2] index=2` |
| Ouvrir propriétés | `rundll32.exe shell32.dll,Control_RunDLL ncpa.cpl` |

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
| Désinstaller une MAJ | Saisie du numéro KB → `wusa /uninstall /kb:[XXXXX] /norestart` |
| Tweak ChrisTitus | Même mécanisme que le menu Système (ps1 temp + `ShellExecuteW runas`) |
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

| Mode | Commande / mécanisme |
|---|---|
| TCP/IP | `socket.create_connection((IP, port))` → envoi bytes ESC/P |
| COM (série) | `serial.Serial(port, baudrate)` → envoi bytes ESC/P (`pyserial`) |
| Couleur rouge | ESC/P : `\x1b\x72\x01` |
| Retour noir | ESC/P : `\x1b\x72\x00` |

---

## Fichiers de configuration

| Fichier | Rôle |
|---|---|
| `version.txt` | Version locale (ex: `2.2.3`) — comparée au serveur pour détecter les MAJ |
| `update_config.txt` | `VERSION_URL` et `DOWNLOAD_URL` pour le système de mise à jour |
| `main.py` ligne `PASSWORDS` | 
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
