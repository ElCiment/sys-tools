# Outils-Système

Application de gestion et d'administration système Windows avec interface graphique moderne basée sur CustomTkinter.

## 📋 Description

Outils-Système est une suite complète d'outils d'administration permettant de gérer, configurer et diagnostiquer des postes de travail Windows. L'application centralise les opérations courantes d'administration système, de gestion réseau, de configuration matériel et de diagnostic.

## 🎯 Fonctionnalités principales

### 📊 Système et Windows

#### Informations système
- Affichage détaillé des spécifications matérielles (CPU, RAM, disques)
- Informations sur le système d'exploitation
- Liste des utilisateurs Windows
- État des connexions réseau
- Monitoring en temps réel

#### Gestion utilisateurs
- Création de nouveaux utilisateurs Windows
- Configuration avec connexion automatique
- Gestion des droits et permissions
- Mot de passe personnalisable

#### Administration Windows
- **Activation Windows** : Script d'activation automatique
- **Renommer le PC** : Renommage du poste avec redémarrage automatique
- **Tweaks Windows** :
  - Désactivation des notifications Windows 10/11
  - Masquage de la zone de recherche (barre des tâches)
  - Masquage de l'icône Task View
  - Centrage des icônes de la barre des tâches (Windows 11)
  - Configuration des heures actives (Windows Update)

### ⚙️ Auto Setup

#### Configuration automatisée de stations
- Setup complet de stations Veloce en un clic
- Configuration automatique de :
  - Nom du PC selon les standards
  - Utilisateur avec auto-login
  - Configuration IP fixe
  - Raccourcis bureau (VELBO/VELSRV)
  - Fond d'écran personnalisé
  - Tweaks Windows standards
- Vérification de connectivité réseau
- Journalisation détaillée de chaque étape

### 🌐 Réseau

#### Diagnostics réseau
- **Vérifier port TCP 40000** : Test de connectivité pour services réseau
- **Voir mots de passe WiFi** : Récupération des profils WiFi sauvegardés
- **Configuration IP** : Outil visuel pour configurer IP fixe/DHCP
  - Sélection de la carte réseau
  - Configuration IP, masque, passerelle
  - Configuration DNS
  - Ouverture directe des propriétés IPv4 Windows

#### Outils réseau avancés
- Test de ping
- Trace route
- Affichage des connexions actives
- Diagnostic de connectivité serveur

### 🖨️ Imprimantes

#### Tests d'impression
- **Test TCP/IP** : Test d'impression réseau sur imprimantes ESC/P
  - Configuration IP et port personnalisables
  - Impression de tickets de test
  - Détection d'imprimantes en ligne
- **Test port série (COM)** : Test d'impression via port série
  - Détection automatique des ports COM disponibles
  - Configuration baudrate, parité, bits de données
  - Support imprimantes thermiques ESC/P

### 🔧 Configuration POS

#### Raccourcis et configuration
- Création automatique de raccourcis bureau (VELBO/VELSRV)
- Configuration serveur personnalisable
- Chemins réseau configurables
- Support multi-stations

### 🔄 Système de mise à jour

#### Mises à jour automatiques
- Vérification automatique au démarrage
- Notification visuelle des mises à jour disponibles
- Téléchargement en un clic avec barre de progression
- Installation automatique et redémarrage de l'application
- URLs de téléchargement configurables (serveur web, Google Drive, GitHub)
- Gestion de version dynamique

## 📦 Installation

### Prérequis
- **Système** : Windows 10/11
- **Python** : 3.10 ou supérieur (pour développement)
- **Droits** : Privilèges administrateur pour certaines fonctions

### Mode développement

1. **Cloner le projet**
   ```bash
   git clone <repository>
   cd Outils-Systeme
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer l'application**
   ```bash
   python main.py
   ```

### Mode production (exe)

1. **Télécharger** l'exécutable `Outils-Systeme.exe`
2. **Double-cliquer** pour lancer
3. Aucune installation requise

## 🚀 Utilisation

### Démarrage
- Lancez `Outils-Systeme.exe` ou `python main.py`
- Entrez le mot de passe d'accès
- L'interface principale s'affiche

### Navigation
- **Menu de gauche** : Sélectionnez la catégorie d'outils
- **Zone centrale** : Options et boutons de la fonctionnalité sélectionnée
- **Console** : Affichage en temps réel des opérations et résultats
- **Menu supérieur** : Accès rapide aux outils Windows et téléchargements

### Fonctions courantes

#### Auto-setup d'une station
1. Sélectionnez "Auto Setup"
2. Renseignez :
   - Serveur (ex: SRV-01)
   - Numéro de station (ex: 01)
3. Cliquez sur "💳 Station Veloce"
4. Suivez la progression dans la console

#### Configuration IP
1. Sélectionnez "Réseau" → "Configuration IP"
2. Choisissez la carte réseau
3. Activez "IP Fixe" et renseignez :
   - Adresse IP
   - Masque de sous-réseau
   - Passerelle par défaut
   - DNS
4. Cliquez sur "Appliquer"

#### Test d'imprimante
1. Sélectionnez "🖨️ Imprimantes" → "Test impression"
2. Choisissez TCP ou COM
3. Configurez les paramètres (IP/Port ou port série)
4. Cliquez sur "Imprimer un test"

## 📁 Structure du projet

```
Outils-Systeme/
├── main.py                    # Point d'entrée principal
├── requirements.txt           # Dépendances Python
├── version.txt               # Numéro de version
├── update_config.txt         # URLs de mise à jour
├── README.md
├── utils/
│   ├── system_utils.py       # Utilitaires système (admin, paths)
│   └── update_manager.py     # Gestion des mises à jour
├── services/
│   ├── printer_service.py    # Gestion imprimantes ESC/P
│   ├── windows_service.py    # Tweaks et configuration Windows
│   └── network_service.py    # Opérations réseau
└── ui/
    ├── password_dialog.py    # Dialogue d'authentification
    └── main_window.py        # Interface principale (4900+ lignes)
```

## 🔧 Configuration

### Changer le numéro de version
1. Éditez `version.txt`
2. Modifiez le numéro (format: x.y.z, ex: 2.2.0)
3. Sauvegardez
4. Recompilez l'application

### Configurer les URLs de mise à jour
1. Éditez `update_config.txt`
2. Modifiez les URLs :
   ```
   VERSION_URL=https://votre-serveur.com/version.txt
   DOWNLOAD_URL=https://votre-serveur.com/Sys-Tools.exe
   ```
3. Sauvegardez et recompilez

**Exemples d'URLs** :
- **GitHub** : `https://github.com/user/repo/releases/download/tag/file.exe`
- **Google Drive** : `https://drive.google.com/uc?export=download&id=FILE_ID`
- **Dropbox** : `https://dl.dropboxusercontent.com/s/abc123/file.exe`

## 🛠️ Compilation

### PyInstaller (recommandé)
```bash
pyinstaller --onefile --noconsole --clean \
    --icon=mainicon2.ico \
    --add-data "version.txt;." \
    --add-data "update_config.txt;." \
    --add-data "mainicon2.ico;." \
    --add-data "assets;assets" \
    --hidden-import=customtkinter \
    --hidden-import=PIL \
    --hidden-import=psutil \
    --hidden-import=pyserial \
    --name "Outils-Systeme" \
    main.py
```

L'exécutable sera créé dans `dist/Outils-Systeme.exe`

**Options importantes** :
- `--clean` : Vide le cache PyInstaller (obligatoire pour voir les changements de version)
- `--onefile` : Un seul fichier exe (tous les fichiers sont embedés)
- `--noconsole` : Pas de fenêtre console

## ⚙️ Architecture technique

### Séparation des responsabilités
- **utils/** : Fonctions utilitaires réutilisables
- **services/** : Logique métier (imprimantes, Windows, réseau)
- **ui/** : Interface graphique et interactions utilisateur

### Technologies utilisées
- **CustomTkinter** : Interface graphique moderne
- **psutil** : Monitoring système
- **pyserial** : Communication série pour imprimantes
- **urllib** : Téléchargement de mises à jour
- **subprocess** : Exécution de commandes système

### Avantages de l'architecture
- Code modulaire et maintenable
- Élimination des duplications
- Gestion d'erreurs cohérente
- Documentation claire avec docstrings
- Facilité de tests et d'extensions

## ⚠️ Avertissements

- **Privilèges administrateur** : La plupart des fonctions nécessitent des droits admin
- **Modifications système** : Les tweaks modifient le registre Windows
- **Code distant** : Certaines fonctions téléchargent et exécutent du code externe
- **Configuration réseau** : La modification d'IP peut couper la connexion
- **Windows uniquement** : Application conçue exclusivement pour Windows

## 🐛 Dépannage

### L'application ne démarre pas
- Vérifiez les droits administrateur
- Assurez-vous que Python 3.10+ est installé
- Vérifiez que toutes les dépendances sont installées

### La mise à jour échoue
- Vérifiez votre connexion Internet
- Assurez-vous que les URLs dans `update_config.txt` sont correctes
- Vérifiez que le fichier distant est accessible
- Fermez complètement l'application avant de réessayer

### Les tweaks Windows ne fonctionnent pas
- Exécutez l'application en tant qu'administrateur
- Vérifiez la version de Windows (certains tweaks sont spécifiques à Win10/11)
- Redémarrez Windows après avoir appliqué les tweaks

## 📝 Notes de développement

### Ajouter une nouvelle fonctionnalité
1. **Service métier** : Créer les fonctions dans `services/`
2. **Interface** : Ajouter l'UI dans `ui/main_window.py`
3. **Menu** : Ajouter l'entrée dans `menu_items`
4. **Tests** : Tester en mode développement
5. **Compilation** : Compiler et distribuer

### Standards de code
- **PEP 8** : Style Python standard
- **Docstrings** : Documentation de toutes les fonctions
- **Gestion d'erreurs** : Try-except avec logs
- **Encodage** : UTF-8 pour tous les fichiers

## 📄 Licence

Usage interne uniquement.

## 👥 Support

Pour questions ou problèmes :
- Consultez ce README
- Vérifiez les logs de la console
- Contactez l'équipe de développement
