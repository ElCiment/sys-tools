# Outils - Système - VERSION COMPLÈTE

## 📦 Installation

### 1. Structure des dossiers

Assurez-vous d'avoir cette structure :

```
.
├── assets/
│   ├── icons/
│   │   └── mainicon.ico      # Icône de l'application
│   ├── images/
│   │   └── mainlogo.png       # Logo (100x100px)
│   └── wallpapers/
│       ├── wallpaper-kpi.jpg
│       ├── wallpaper-jinctech.png
│       └── wallpaper-Tamio.jpg
├── config/
│   ├── releasesnotes.txt
│   ├── README_PSEXEC.txt
│   └── psexec.exe             # À télécharger
├── services/
├── ui/
├── utils/
├── main.py
└── requirements.txt
```

### 2. Assets nécessaires

**Téléchargez et placez ces fichiers :**

1. **mainicon.ico** : Icône de l'application → `assets/icons/`
2. **mainlogo.png** : Logo 100x100px → `assets/images/`
3. **Wallpapers** (3 fichiers) → `assets/wallpapers/`
4. **psexec.exe** (optionnel) : https://learn.microsoft.com/en-us/sysinternals/downloads/psexec → `config/`

### 3. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancement

```bash
python main.py
```

**Mot de passe :** `Log1tech`

## 🎯 Fonctionnalités complètes

### ✅ TOUTES les fonctionnalités du code original

- ✅ Auto Setup (Poste Standard, Serveur, Station Veloce)
- ✅ Commandes personnalisées avec PsExec
- ✅ Configuration IP avancée (DHCP/Statique)
- ✅ Gestion utilisateurs Windows (avec auto-login)
- ✅ Tweaks Windows complets
- ✅ Wallpaper (3 choix)
- ✅ WiFi passwords
- ✅ Test impression ESC/P
- ✅ Raccourcis VELBO/VELSRV
- ✅ TeamViewer/AnyDesk IDs
- ✅ Renommer PC
- ✅ Activation Windows
- ✅ Informations système détaillées

## 📝 Notes importantes

- **Windows uniquement** (utilise winreg, ctypes.windll)
- **Droits admin** requis pour certaines fonctions
- **Architecture modulaire** : utils/, services/, ui/

## 🔧 Compilation avec PyInstaller

```bash
pyinstaller --onefile --windowed \
  --icon="assets/icons/mainicon.ico" \
  --add-data "assets;assets" \
  --add-data "config;config" \
  --name "Outils-Systeme" \
  main.py
```

## 📞 Support

Pour toute question : https://kpi-tech.ca
