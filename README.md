# Outils - Système

Application de gestion système Windows avec interface graphique moderne basée sur CustomTkinter.

## 🎯 Fonctionnalités

### 📊 Système/Windows
- **Informations système** : Affiche CPU, RAM, utilisateurs, disques
- **Activer Windows** : Script d'activation automatique
- **Renommer le PC** : Renommage facile avec redémarrage
- **Tweaks Windows** : Optimisations de la barre des tâches, désactivation notifications
- **Gérer les utilisateurs** : Création et gestion d'utilisateurs Windows

### 💳 POS
- **Créer raccourcis VELBO/VELSRV** : Création automatique de raccourcis bureau

### 🌐 Réseau
- **Vérifier port TCP 40000** : Test de connectivité réseau
- **Voir mots de passe WiFi** : Récupération des profils WiFi sauvegardés

### 🖨️ Imprimantes
- **Test impression** : Test TCP/IP ou port série pour imprimantes ESC/P

## 📦 Installation

### Prérequis
- Python 3.11 ou supérieur
- Windows (pour les fonctionnalités d'administration)

### Installation des dépendances
```bash
pip install -r requirements.txt
```

## 🚀 Utilisation

### Lancement de l'application
```bash
python main.py
```

### Mot de passe par défaut
```
Log1tech
```

### Mode sans mot de passe (développement uniquement)
```bash
python main.py --skip-password
```

## 📁 Structure du projet

```
.
├── main.py                 # Point d'entrée principal
├── requirements.txt        # Dépendances Python
├── README.md              # Documentation
├── utils/                 # Utilitaires système
│   ├── __init__.py
│   └── system_utils.py    # Fonctions système (admin, paths, etc.)
├── services/              # Services métier
│   ├── __init__.py
│   ├── printer_service.py  # Gestion imprimantes ESC/P
│   ├── windows_service.py  # Tweaks et gestion Windows
│   └── network_service.py  # Opérations réseau
└── ui/                    # Interface utilisateur
    ├── __init__.py
    ├── password_dialog.py  # Dialogue d'authentification
    └── main_window.py      # Fenêtre principale
```

## 🔧 Architecture

Le code a été refactorisé pour suivre les bonnes pratiques :

### Séparation des responsabilités
- **utils/** : Fonctions utilitaires réutilisables
- **services/** : Logique métier (imprimantes, Windows, réseau)
- **ui/** : Interface graphique (dialogues, fenêtre principale)

### Avantages de la refactorisation
- ✅ Code modulaire et maintenable
- ✅ Élimination des duplications
- ✅ Gestion d'erreurs cohérente
- ✅ Documentation claire avec docstrings
- ✅ Facilité de tests et d'extensions

## 🛠️ Développement

### Ajout de nouvelles fonctionnalités

1. **Service métier** : Ajouter dans `services/`
2. **Interface utilisateur** : Ajouter dans `ui/main_window.py`
3. **Menu** : Modifier `menu_items` dans `_create_left_menu()`

### Standards de code
- **PEP 8** : Style Python standard
- **Docstrings** : Documentation de toutes les fonctions publiques
- **Type hints** : Optionnel mais recommandé
- **Gestion d'erreurs** : Try-except avec logs appropriés

## ⚠️ Avertissements

- **Privilèges administrateur** : Certaines fonctions nécessitent des droits admin
- **Code distant** : L'activation Windows télécharge et exécute du code externe
- **Modifications système** : Les tweaks modifient le registre Windows

## 📝 Changelog

### Version 2.0 (Refactorisation)
- ✨ Architecture modulaire complète
- ✨ Séparation utils/services/ui
- ✨ Élimination du code dupliqué
- ✨ Documentation améliorée
- ✨ Gestion d'erreurs standardisée
- ✨ Code plus maintenable et testable

### Version 1.x (Original)
- Fonctionnalités de base
- Monolithe de 3267 lignes

## 📄 Licence

Usage interne uniquement.

## 👥 Support

Pour toute question ou problème, consultez la documentation ou contactez l'équipe de développement.
