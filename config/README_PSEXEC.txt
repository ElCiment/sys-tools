PSEXEC - EXÉCUTION DE COMMANDES À DISTANCE
==========================================

PsExec est un outil Microsoft Sysinternals permettant d'exécuter 
des commandes à distance sur d'autres machines Windows.

PLACEMENT DU FICHIER:
---------------------
Placer "psexec.exe" dans ce dossier config/ ou dans le PATH système.

TÉLÉCHARGEMENT:
--------------
Site officiel: https://learn.microsoft.com/en-us/sysinternals/downloads/psexec

UTILISATION DANS L'APPLICATION:
-------------------------------
1. Aller dans "Commandes personnalisées"
2. Cocher "Via PsExec"
3. Entrer l'IP/nom de l'hôte distant
4. Optionnel: credentials (utilisateur/mot de passe)
5. Entrer la commande à exécuter

EXEMPLE:
--------
Commande: ipconfig /all
Hôte: 192.168.1.100
User: admin
Password: ********

NOTES DE SÉCURITÉ:
-----------------
• PsExec nécessite des droits admin sur la machine distante
• Les credentials sont envoyés en clair sur le réseau local
• Utilisez uniquement sur des réseaux de confiance

© Microsoft Corporation - Sysinternals
