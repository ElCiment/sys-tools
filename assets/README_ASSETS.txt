STRUCTURE DES ASSETS
====================

📁 assets/
│
├── 📁 icons/
│   ├── mainicon.ico          # Icône principale de l'application
│   └── ...
│
├── 📁 wallpapers/
│   ├── wallpaper-kpi.jpg     # Wallpaper KPI-Tech
│   ├── wallpaper-jinctech.png # Wallpaper JincTech
│   └── wallpaper-Tamio.jpg   # Wallpaper Tamio
│
└── 📁 images/
    └── mainlogo.png          # Logo principal (100x100px)

📁 config/
│
├── releasesnotes.txt         # Notes de version
├── README_PSEXEC.txt         # Documentation PsExec
└── psexec.exe                # (À télécharger séparément)

INSTRUCTIONS:
-------------

1. **Icônes**:
   - Placer mainicon.ico dans assets/icons/
   - Format: ICO, 256x256px recommandé

2. **Wallpapers**:
   - Placer les fichiers .jpg/.png dans assets/wallpapers/
   - Résolution recommandée: 1920x1080 ou supérieur

3. **Logo**:
   - Placer mainlogo.png dans assets/images/
   - Format: PNG avec transparence, 100x100px

4. **PsExec**:
   - Télécharger depuis Microsoft Sysinternals
   - Placer psexec.exe dans config/
   - Ou installer dans le PATH système

POUR PYINSTALLER:
-----------------
Lors de la compilation de l'exe, ajouter ces dossiers:
  --add-data "assets;assets"
  --add-data "config;config"
