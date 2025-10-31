"""
Fenêtre principale de l'application
Interface utilisateur principale avec menu latéral et console intégrée
"""
import os
import sys
import time
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import webbrowser
import subprocess
import re
import psutil

from utils.system_utils import get_base_path, is_admin, relaunch_as_admin
from services.printer_service import build_message, send_tcp, send_serial, get_serial_ports
from services.windows_service import (
    tweak_taskbar, restore_context_menu, uninstall_kb5064081,
    disable_windows_notifications, apply_wallpaper, rename_computer,
    add_windows_user, create_veloce_shortcuts, restore_context_menu_win11)
from services.network_service import check_tcp_port, get_wifi_passwords, get_teamviewer_id, get_anydesk_id, show_wifi_passwords
from utils.update_manager import (check_for_updates, download_update, 
                                   install_update, get_remote_version,
                                   LOCAL_VERSION)


class ToolsApp(ctk.CTk):
    """Fenêtre principale de l'application Outils - Système"""

    def __init__(self):
        super().__init__()

        self.title("Outils - Système")
        base_path = get_base_path()

        # Icône de l'application
        icon_path = os.path.join(base_path, "mainicon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"Impossible de charger l'icône: {e}")

        # Configuration de la grille
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initialisation des variables
        self._init_variables()

        # Création de l'interface
        self._create_menu_bar()
        self._create_header()
        self._create_left_menu()
        self._create_main_area()

        # Log initial
        self.log(
            f"Application démarrée. Admin: {'Oui' if is_admin() else 'Non'}")

        # Maximiser la fenêtre après la création complète de l'interface
        self.after(100, lambda: self.state("zoomed"))

        # Récupération des IDs en arrière-plan
        threading.Thread(target=self._update_remote_ids, daemon=True).start()

    def _init_variables(self):
        """Initialise les variables de l'application"""
        self.print_text_var = ctk.StringVar(
            value="------ Test d'impression ------")
        self.mode_var = tk.StringVar(value="tcp")
        self.com_var = tk.StringVar(value="")
        self.repeat_var = tk.StringVar(value="1")
        self.lines_var = tk.StringVar(value="20")
        self.ip_var = tk.StringVar(value="192.168.192.168")
        self.port_var = tk.StringVar(value="9100")
        self.baud_var = tk.StringVar(value="115200")
        self.shortcut_folder_var = tk.StringVar(value=r"C:\veloce")
        self.check_host_var = tk.StringVar(value="127.0.0.1")
        self.check_port_var = tk.StringVar(value="40000")
        self.wallpaper_var = tk.StringVar(value="wallpaper-kpi.jpg")
        self.pc_name_var = tk.StringVar(
            value=os.environ.get("COMPUTERNAME", ""))

    def _create_menu_bar(self):
        """Crée la barre de menu"""
        menubar = tk.Menu(self, tearoff=0, font=("Segoe UI", 12))

        # Menu Fichier
        fichier_menu = tk.Menu(menubar, tearoff=0, font=("Segoe UI", 12))
        fichier_menu.add_separator()
        fichier_menu.add_command(label="❌ Quitter", command=self.quit)
        menubar.add_cascade(label="Fichier", menu=fichier_menu)

        # Menu Outils
        outils_menu = tk.Menu(menubar, tearoff=0, font=("Segoe UI", 12))
        outils_menu.add_command(label="⚙️ Panneau de configuration",
                                command=lambda: os.system("control"))
        outils_menu.add_command(label="🖥️ Gérer l'ordinateur",
                                command=lambda: os.system("compmgmt.msc"))
        outils_menu.add_command(label="📊 Gestionnaire des tâches",
                                command=lambda: os.system("taskmgr"))
        outils_menu.add_separator()
        outils_menu.add_command(label="🧩 Programmes et fonctionnalités",
                                command=lambda: os.system("appwiz.cpl"))
        outils_menu.add_command(
            label="🔄 Windows Update",
            command=lambda: os.system("control /name Microsoft.WindowsUpdate"))
        outils_menu.add_command(label="🌐 Connexions réseau",
                                command=lambda: os.system("ncpa.cpl"))
        menubar.add_cascade(label="Outils", menu=outils_menu)

        # Menu Système
        system_menu = tk.Menu(menubar, tearoff=0, font=("Segoe UI", 12))
        system_menu.add_command(label="📁 Explorateur",
                                command=lambda: os.system("explorer"))
        system_menu.add_command(label="🧾 Informations système",
                                command=lambda: os.system("msinfo32"))
        system_menu.add_command(label="⚡ PowerShell",
                                command=lambda: os.system("powershell"))
        system_menu.add_separator()
        system_menu.add_command(label="🧠 Registre Windows",
                                command=lambda: os.system("regedit"))
        system_menu.add_command(label="🧰 Services Windows",
                                command=lambda: os.system("services.msc"))
        system_menu.add_command(label="🚀 Configuration du système",
                                command=lambda: os.system("msconfig"))
        system_menu.add_separator()
        system_menu.add_command(
            label="🗂️ Dossier Démarrage",
            command=lambda: os.system("explorer shell:startup"))
        menubar.add_cascade(label="Système", menu=system_menu)

        # Menu Aide
        aide_menu = tk.Menu(menubar, tearoff=0, font=("Segoe UI", 12))
        aide_menu.add_command(label="📄 Release Notes",
                              command=self.show_release_notes)
        aide_menu.add_command(
            label="🌐 Téléchargements",
            command=lambda: webbrowser.open(
                "https://kpi-tech.ca/launcher/telechargements.html"))
        menubar.add_cascade(label="Aide", menu=aide_menu)

        self.config(menu=menubar)

    def _get_veloce_password(self):
        """Calcule le mot de passe Veloce du jour"""
        from datetime import datetime
        now = datetime.now()

        # Mapping des chiffres aux lettres
        digit_to_letter = {
            '0': 'A',
            '1': 'B',
            '2': 'C',
            '3': 'D',
            '4': 'E',
            '5': 'F',
            '6': 'G',
            '7': 'H',
            '8': 'I',
            '9': 'J'
        }

        # Récupérer le dernier chiffre de chaque composant
        day_last = str(now.day)[-1]
        month_last = str(now.month)[-1]
        year_last = str(now.year)[-1]

        # Construire le mot de passe: (Jour)V(Mois)E(Année)L
        password = (digit_to_letter[day_last] + 'V' +
                    digit_to_letter[month_last] + 'E' +
                    digit_to_letter[year_last] + 'L')

        return password

    def _create_header(self):
        """Crée l'en-tête de l'application"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0,
                    column=0,
                    columnspan=4,
                    sticky="nsew",
                    padx=12,
                    pady=(12, 4))
        header.grid_columnconfigure(1, weight=1)

        # Logo
        base_path = get_base_path()
        logo_path = os.path.join(base_path, "assets", "images", "mainlogo.png")
        if os.path.exists(logo_path):
            try:
                logo_image = Image.open(logo_path).resize(
                    (100, 100), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = ctk.CTkLabel(header,
                                          image=self.logo_photo,
                                          text="")
                logo_label.grid(row=0,
                                column=0,
                                rowspan=3,
                                sticky="w",
                                padx=(0, 10))
            except Exception as e:
                print(f"Impossible de charger le logo: {e}")

        # Titre
        title = ctk.CTkLabel(header,
                             text="Outils - Système",
                             font=ctk.CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=1, sticky="w", pady=(4, 0))

        # Frame pour version + bouton mise à jour (côte à côte)
        version_frame = ctk.CTkFrame(header, fg_color="transparent")
        version_frame.grid(row=1, column=1, sticky="w")

        # Version (chargée depuis le serveur)
        self.version_label = ctk.CTkLabel(version_frame,
                               text=f"Version {LOCAL_VERSION}",
                               font=ctk.CTkFont(size=12))
        self.version_label.pack(side="left", padx=(0, 10))

        # Bouton vérifier mises à jour (à côté de la version)
        update_btn = ctk.CTkButton(version_frame,
                                   text="🔄 Mise à jour",
                                   width=110,
                                   height=24,
                                   command=self._check_updates_manual,
                                   fg_color="#0284c7",
                                   hover_color="#0369a1",
                                   font=ctk.CTkFont(size=10))
        update_btn.pack(side="left")

        # Lancer la vérification automatique au démarrage
        threading.Thread(target=self._check_updates_auto, daemon=True).start()

        # Mot de passe Veloce du jour
        veloce_pwd = self._get_veloce_password()
        pwd_label = ctk.CTkLabel(
            header,
            text=f"🔑 Password Veloce du jour: {veloce_pwd}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#4ade80")
        pwd_label.grid(row=2, column=1, sticky="w", pady=(2, 0))

        # TeamViewer et AnyDesk IDs (affichés en permanence)
        self.tv_label = ctk.CTkLabel(header,
                                     text="TeamViewer ID: Chargement...",
                                     font=ctk.CTkFont(size=11),
                                     text_color="gray")
        self.tv_label.grid(row=0, column=2, sticky="e", padx=(10, 0))

        self.ad_label = ctk.CTkLabel(header,
                                     text="AnyDesk ID: Chargement...",
                                     font=ctk.CTkFont(size=11),
                                     text_color="gray")
        self.ad_label.grid(row=1, column=2, sticky="e", padx=(10, 0))

        # Bouton Effacer console
        clear_btn = ctk.CTkButton(header,
                                  text="🗑️ Effacer console",
                                  width=140,
                                  command=self.clear_console,
                                  fg_color="#c03a3a",
                                  hover_color="#e05454")
        clear_btn.grid(row=2, column=2, sticky="e", pady=(5, 0))

    def _create_left_menu(self):
        """Crée le menu latéral gauche"""
        left = ctk.CTkScrollableFrame(self, width=260, corner_radius=8)
        left.grid(row=1, column=0, sticky="nsw", padx=(12, 6), pady=8)

        lbl = ctk.CTkLabel(left,
                           text="Fonctions",
                           font=ctk.CTkFont(size=14, weight="bold"))
        lbl.pack(anchor="nw", padx=12, pady=(12, 6))

        # Menu items avec sections
        menu_items = [
            ("⚙️ Setup", None),
            ("Auto Setup", "auto_setup"),
            ("📊 Système/Windows", None),
            ("Infos Système", "show_system_info"),
            ("Activer Windows", "activate_windows"),
            ("Renommer le PC", "rename_pc"),
            ("Tweaks Windows", "tweak_windows"),
            ("Gérer les Utilisateurs", "manage_users"),
            ("Commandes personnalisées", "custom_commands"),
            #("💳 POS", None),
            #("Créer raccourcis VELBO/VELSRV", "create_shortcuts"),
            ("🌐 Réseau", None),
            ("Vérifier port TCP 40000", "check_port"),
            ("Voir mots de passe WiFi", "show_wifi_passwords"),
            ("Adresse IP", "ip_config"),
            ("🖨️ Imprimantes", None),
            ("Test impression", "print_test"),
        ]

        for txt, key in menu_items:
            if key is None:
                # Titre de section
                lbl = ctk.CTkLabel(left,
                                   text=txt,
                                   font=ctk.CTkFont(size=12, weight="bold"))
                lbl.pack(anchor="nw", padx=12, pady=(12, 4))
                # Ligne de séparation
                separator = ctk.CTkFrame(left, height=1, fg_color="#555555")
                separator.pack(fill="x", padx=12, pady=(0, 8))
            else:
                b = ctk.CTkButton(left,
                                  text=txt,
                                  width=220,
                                  height=44,
                                  fg_color="#c03a3a",
                                  hover_color="#e05454",
                                  command=lambda k=key: self.show_function(k))
                b.pack(padx=12, pady=6, anchor="n")

    def _create_main_area(self):
        """Crée la zone principale (console + options) avec panneau resizable"""
        main = ctk.CTkFrame(self)
        main.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=8)
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # Utiliser PanedWindow pour rendre le panneau du bas resizable
        paned = tk.PanedWindow(main,
                               orient=tk.VERTICAL,
                               sashwidth=6,
                               bg="#2b2b2b",
                               sashrelief=tk.RAISED)
        paned.grid(row=0, column=0, sticky="nsew")

        # Frame du haut: Console
        top_frame = ctk.CTkFrame(paned)
        paned.add(top_frame, minsize=150)

        # Console title
        cons_title = ctk.CTkLabel(top_frame,
                                  text="Journal / Console",
                                  font=ctk.CTkFont(size=12, weight="bold"))
        cons_title.pack(anchor="w", padx=8, pady=(8, 2))

        # Console textbox
        self.log_box = ctk.CTkTextbox(top_frame,
                                      wrap="word",
                                      font=("Courier New", 12))
        self.log_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.log_box.configure(state="disabled")

        # Frame du bas: Options dynamiques (resizable)
        bottom_frame = ctk.CTkFrame(paned, corner_radius=8)
        paned.add(bottom_frame, minsize=100)

        self.func_options_holder = ctk.CTkFrame(bottom_frame,
                                                fg_color="transparent")
        self.func_options_holder.pack(fill="both", expand=True, padx=8, pady=8)

    def log(self, message):
        """Ajoute un message au journal de la console"""
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{ts}] {message}\n"
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def clear_console(self):
        """Efface le contenu de la console"""
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        self.log("Console effacée")

    def show_function(self, func_key):
        """Affiche l'interface d'une fonction"""
        # Nettoyer l'ancien contenu
        for widget in self.func_options_holder.winfo_children():
            widget.destroy()

        # Appeler la fonction correspondante
        if func_key == "print_test":
            self._build_print_options(self.func_options_holder)
        elif func_key == "check_port":
            self._build_checkport_options(self.func_options_holder)
        elif func_key == "show_wifi_passwords":
            self._build_wifi_options(self.func_options_holder)
        elif func_key == "tweak_windows":
            self._build_tweak_options(self.func_options_holder)
        elif func_key == "rename_pc":
            self._build_rename_pc_options(self.func_options_holder)
        elif func_key == "activate_windows":
            self._build_activate_windows_options(self.func_options_holder)
        elif func_key == "show_system_info":
            self._show_system_info()
        elif func_key == "create_shortcuts":
            self._build_shortcuts_options(self.func_options_holder)
        elif func_key == "manage_users":
            self._build_manage_users_options(self.func_options_holder)
        elif func_key == "auto_setup":
            self.build_auto_setup_options(self.func_options_holder)
        elif func_key == "custom_commands":
            self.build_custom_commands_options(self.func_options_holder)
        elif func_key == "ip_config":
            self.build_ip_config_options(self.func_options_holder)
        else:
            self.log(f"Fonction '{func_key}' non implémentée")

    def _build_print_options(self, parent):
        """Construit l'interface de test d'impression"""
        f = ctk.CTkFrame(parent)
        f.pack(fill="both", expand=True)

        # Mode de communication
        row_frame = ctk.CTkFrame(f, fg_color="transparent")
        row_frame.pack(anchor="nw", fill="x", pady=(4, 8))
        ctk.CTkLabel(row_frame,
                     text="Mode de communication:").pack(side="left",
                                                         padx=(4, 8))
        mode_combo = ctk.CTkOptionMenu(row_frame,
                                       values=["tcp", "com"],
                                       variable=self.mode_var,
                                       width=120)
        mode_combo.pack(side="left")

        # Conteneur pour TCP/COM
        self.conn_frame = ctk.CTkFrame(f)
        self.conn_frame.pack(fill="x", padx=6, pady=(6, 4))
        self.conn_frame.grid_propagate(False)
        self.conn_frame.configure(height=130)

        # TCP Frame
        self.tcp_frame = ctk.CTkFrame(self.conn_frame)
        self.tcp_frame.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.tcp_frame,
                     text="Connexion TCP/IP",
                     font=ctk.CTkFont(weight="bold")).grid(row=0,
                                                           column=0,
                                                           sticky="w",
                                                           padx=6,
                                                           pady=6)
        ctk.CTkLabel(self.tcp_frame, text="Adresse IP:").grid(row=1,
                                                              column=0,
                                                              sticky="w",
                                                              padx=6,
                                                              pady=4)
        ctk.CTkEntry(self.tcp_frame, textvariable=self.ip_var,
                     width=220).grid(row=1,
                                     column=1,
                                     sticky="w",
                                     padx=6,
                                     pady=4)
        ctk.CTkLabel(self.tcp_frame, text="Port:").grid(row=2,
                                                        column=0,
                                                        sticky="w",
                                                        padx=6,
                                                        pady=4)
        ctk.CTkEntry(self.tcp_frame, textvariable=self.port_var,
                     width=120).grid(row=2,
                                     column=1,
                                     sticky="w",
                                     padx=6,
                                     pady=4)

        # COM Frame
        self.com_frame = ctk.CTkFrame(self.conn_frame)
        self.com_frame.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.com_frame,
                     text="Connexion Série (COM)",
                     font=ctk.CTkFont(weight="bold")).grid(row=0,
                                                           column=0,
                                                           sticky="w",
                                                           padx=6,
                                                           pady=6)
        ctk.CTkLabel(self.com_frame, text="Port COM:").grid(row=1,
                                                            column=0,
                                                            sticky="w",
                                                            padx=6,
                                                            pady=4)

        ports = get_serial_ports()
        self.com_option = ctk.CTkOptionMenu(
            self.com_frame,
            values=ports if ports else ["Aucun détecté"],
            variable=self.com_var,
            width=220)
        self.com_option.grid(row=1, column=1, sticky="w", padx=6, pady=4)

        ctk.CTkButton(self.com_frame,
                      text="🔄 Rafraîchir",
                      width=120,
                      command=self._refresh_com_ports).grid(row=1,
                                                            column=2,
                                                            padx=6,
                                                            pady=4)

        ctk.CTkLabel(self.com_frame, text="Baudrate:").grid(row=2,
                                                            column=0,
                                                            sticky="w",
                                                            padx=6,
                                                            pady=4)
        baud_rates = ["9600", "19200", "38400", "57600", "115200"]
        self.baud_menu = ctk.CTkOptionMenu(self.com_frame,
                                           values=baud_rates,
                                           variable=self.baud_var,
                                           width=120)
        self.baud_menu.grid(row=2, column=1, sticky="w", padx=6, pady=4)

        # Options
        opts = ctk.CTkFrame(f, fg_color="transparent")
        opts.pack(fill="x", padx=6, pady=(10, 6))
        ctk.CTkLabel(opts, text="Répétitions:").grid(row=0,
                                                     column=0,
                                                     padx=6,
                                                     pady=6,
                                                     sticky="w")
        ctk.CTkEntry(opts, textvariable=self.repeat_var,
                     width=80).grid(row=0,
                                    column=1,
                                    padx=6,
                                    pady=6,
                                    sticky="w")

        ctk.CTkLabel(opts, text="Lignes par section:").grid(row=1,
                                                            column=0,
                                                            padx=6,
                                                            pady=6,
                                                            sticky="w")
        ctk.CTkEntry(opts, textvariable=self.lines_var,
                     width=80).grid(row=1,
                                    column=1,
                                    padx=6,
                                    pady=6,
                                    sticky="w")

        ctk.CTkButton(opts,
                      text="🚀 Envoyer le test",
                      width=160,
                      command=self._run_print_test).grid(row=0,
                                                         column=2,
                                                         rowspan=2,
                                                         padx=12,
                                                         pady=6)

        # Texte à imprimer
        text_frame = ctk.CTkFrame(f, fg_color="transparent")
        text_frame.pack(fill="x", padx=6, pady=(6, 4))
        ctk.CTkLabel(text_frame, text="Texte à imprimer:").grid(row=0,
                                                                column=0,
                                                                sticky="w",
                                                                padx=6,
                                                                pady=4)
        ctk.CTkEntry(text_frame, textvariable=self.print_text_var,
                     width=400).grid(row=0,
                                     column=1,
                                     sticky="w",
                                     padx=6,
                                     pady=4)

        # Toggle TCP/COM
        def toggle():
            if self.mode_var.get() == "tcp":
                self.com_frame.grid_remove()
                self.tcp_frame.grid()
            else:
                self.tcp_frame.grid_remove()
                self.com_frame.grid()

        self.mode_var.trace_add("write", lambda *_: toggle())
        toggle()

    def _build_checkport_options(self, parent):
        """Construit l'interface de vérification de port"""
        f = ctk.CTkFrame(parent)
        f.pack(fill="both", expand=True, padx=6, pady=6)
        ctk.CTkLabel(f,
                     text="Vérifier si le port TCP 40000 est ouvert",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w",
                                                           pady=(0, 6))

        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(anchor="w", pady=(6, 8))
        ctk.CTkLabel(row, text="Hôte:").pack(side="left")
        ctk.CTkEntry(row, textvariable=self.check_host_var,
                     width=140).pack(side="left", padx=(4, 12))
        ctk.CTkLabel(row, text="Port:").pack(side="left")
        ctk.CTkEntry(row, textvariable=self.check_port_var,
                     width=80).pack(side="left", padx=(4, 0))

        ctk.CTkButton(f,
                      text="Tester le port",
                      width=200,
                      command=self._run_check_port).pack(pady=6)

    def _build_wifi_options(self, parent):
        """Construit l'interface de récupération des mots de passe WiFi"""
        f = ctk.CTkFrame(parent)
        f.pack(fill="both", expand=True, padx=6, pady=6)
        ctk.CTkLabel(f,
                     text="Voir les mots de passe WiFi sauvegardés",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w",
                                                           pady=(0, 6))
        ctk.CTkLabel(
            f,
            text=
            "Récupère tous les profils WiFi enregistrés et leurs mots de passe.",
            text_color="#a8b3c6").pack(anchor="w", pady=(0, 6))
        ctk.CTkButton(f,
                      text="🔍 Récupérer les mots de passe WiFi",
                      width=280,
                      command=self._run_show_wifi_passwords).pack(pady=6)

    def _build_tweak_options(self, parent):
        """Construit l'interface des tweaks Windows"""
        f = ctk.CTkFrame(parent)
        f.pack(fill="both", expand=True, padx=6, pady=6)
        ctk.CTkLabel(f,
                     text="Tweaks Windows & Options",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w",
                                                           pady=(0, 6))

        ctk.CTkButton(f,
                      text="Appliquer Tweaks Taskbar",
                      width=220,
                      fg_color="#4c84e0",
                      hover_color="#2e62c9",
                      command=self._run_tweak_taskbar).pack(anchor="w",
                                                            pady=(0, 8))
        ctk.CTkButton(f,
                      text="Désactiver notifications Windows",
                      width=260,
                      fg_color="#4c84e0",
                      hover_color="#2e62c9",
                      command=self._run_disable_notifications).pack(anchor="w",
                                                                    pady=(0,
                                                                          8))
        ctk.CTkButton(f,
                      text="Rétablir Right Click Menu (Win11)",
                      width=260,
                      fg_color="#4c84e0",
                      hover_color="#2e62c9",
                      command=self._run_restore_menu).pack(anchor="w",
                                                           pady=(0, 20))
        ctk.CTkButton(f,
                      text="🧩 Désinstaller KB5064081",
                      width=240,
                      fg_color="#e05454",
                      hover_color="#c03a3a",
                      command=self._run_uninstall_kb).pack(anchor="w",
                                                           pady=(0, 20))

        # Sélecteur de wallpaper
        ctk.CTkLabel(f,
                     text="🖼️ Appliquer un fond d'écran:",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w",
                                                           pady=(0, 6))

        # Détecter les wallpapers disponibles
        base_path = get_base_path()
        wallpaper_dir = os.path.join(base_path, "assets", "wallpapers")
        wallpapers = []
        if os.path.exists(wallpaper_dir):
            for file in os.listdir(wallpaper_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    wallpapers.append(file)

        if not wallpapers:
            wallpapers = ["wallpaper-kpi.jpg"]  # Défaut

        # Variable pour le wallpaper sélectionné
        if not hasattr(self, 'selected_wallpaper_var'):
            self.selected_wallpaper_var = tk.StringVar(
                value=wallpapers[0] if wallpapers else "")

        # Frame pour le sélecteur
        wallpaper_frame = ctk.CTkFrame(f, fg_color="transparent")
        wallpaper_frame.pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(wallpaper_frame, text="Wallpaper:").pack(side="left",
                                                              padx=(0, 8))
        wallpaper_menu = ctk.CTkOptionMenu(
            wallpaper_frame,
            variable=self.selected_wallpaper_var,
            values=wallpapers,
            width=300)
        wallpaper_menu.pack(side="left", padx=(0, 8))

        ctk.CTkButton(wallpaper_frame,
                      text="Appliquer",
                      width=120,
                      fg_color="#16a34a",
                      hover_color="#15803d",
                      command=self._run_apply_wallpaper).pack(side="left")

    def _build_rename_pc_options(self, parent):
        """Construit l'interface de renommage du PC"""
        f = ctk.CTkFrame(parent)
        f.pack(fill="both", expand=True, padx=6, pady=6)
        ctk.CTkLabel(f,
                     text="Renommer ce PC Windows",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w",
                                                           pady=(0, 6))

        ctk.CTkLabel(f, text="Nouveau nom du PC:").pack(anchor="w",
                                                        pady=(4, 2))
        ctk.CTkEntry(f, textvariable=self.pc_name_var,
                     width=300).pack(anchor="w", pady=(0, 6))

        ctk.CTkButton(f,
                      text="Renommer le PC",
                      width=220,
                      fg_color="#2b6ee6",
                      hover_color="#2058c9",
                      command=self._run_rename_pc).pack(pady=6)
        ctk.CTkLabel(f,
                     text="⚠️ Nécessite un redémarrage",
                     text_color="#fca5a5").pack(anchor="w", pady=(6, 0))

    def _build_activate_windows_options(self, parent):
        """Construit l'interface d'activation Windows"""
        f = ctk.CTkFrame(parent)
        f.pack(fill="both", expand=True, padx=6, pady=6)
        ctk.CTkLabel(f,
                     text="Activer Windows:",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w",
                                                           pady=(0, 6))

        fixed_cmd = 'irm https://get.activated.win| iex'
        ctk.CTkLabel(f,
                     text="Commande (non modifiable):",
                     text_color="#a8b3c6").pack(anchor="w")
        cmd_box = ctk.CTkTextbox(f, width=900, height=60, wrap="word")
        cmd_box.insert("0.0", fixed_cmd)
        cmd_box.configure(state="disabled")
        cmd_box.pack(fill="x", pady=(6, 8))

        ctk.CTkButton(
            f,
            text="▶ Activer Windows",
            width=280,
            fg_color="#2b6ee6",
            hover_color="#2058c9",
            command=lambda: self._run_activate_windows(fixed_cmd)).pack(pady=6)
        ctk.CTkLabel(
            f,
            text="⚠️ Cette commande télécharge et exécute du code distant.",
            text_color="#fca5a5").pack(anchor="w", pady=(8, 0))

    def _build_shortcuts_options(self, parent):
        """Construit l'interface de création de raccourcis"""
        f = ctk.CTkFrame(parent)
        f.pack(fill="both", expand=True, padx=6, pady=6)
        ctk.CTkLabel(f,
                     text="Créer sur le Bureau : VELBO.lnk et VELSRV.lnk",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w",
                                                           pady=(0, 6))
        ctk.CTkLabel(f,
                     text="Dossier contenant velbo.exe et velsrv.exe :").pack(
                         anchor="w")
        folder_entry = ctk.CTkEntry(f,
                                    textvariable=self.shortcut_folder_var,
                                    width=520)
        folder_entry.pack(anchor="w", pady=(6, 8))
        ctk.CTkButton(f,
                      text="Créer les raccourcis",
                      width=220,
                      command=self._run_create_shortcuts).pack(pady=(4, 8))

    def _refresh_com_ports(self):
        """Rafraîchit la liste des ports COM"""
        ports = get_serial_ports()
        vals = ports if ports else ["Aucun détecté"]
        try:
            self.com_option.configure(values=vals)
            if ports:
                self.com_option.set(ports[0])
        except Exception:
            pass
        self.log(
            f"🔄 Ports COM disponibles: {', '.join(ports) if ports else 'Aucun détecté'}"
        )

    def _run_print_test(self):
        """Exécute le test d'impression"""
        try:
            repeat = int(self.repeat_var.get().strip() or 1)
            lines = int(self.lines_var.get().strip() or 20)
        except Exception:
            self.log("⚠️ Valeurs de répétitions/lignes invalides")
            return

        text_to_print = self.print_text_var.get().strip() or "Test Test Test"
        mode = self.mode_var.get()
        ip = self.ip_var.get().strip()
        port = self.port_var.get().strip()
        com_port = self.com_var.get().strip()
        baud = self.baud_var.get().strip()

        data = build_message(n_lines_each=lines,
                             text=text_to_print,
                             mode=mode,
                             ip=ip,
                             port=port,
                             com_port=com_port,
                             baud=baud)

        self.log(f"--- DÉBUT DU TEST ({mode.upper()}) ---")

        def worker():
            for i in range(repeat):
                self.log(f"Exécution {i+1}/{repeat}...")
                if mode.lower() == "tcp":
                    try:
                        port_num = int(port or 9100)
                    except:
                        port_num = 9100
                    send_tcp(ip, port_num, data, self.log)
                else:
                    if not com_port or com_port == "Aucun détecté":
                        self.log("⚠️ Aucun port COM sélectionné")
                        return
                    try:
                        baud_num = int(baud or 9600)
                    except:
                        baud_num = 9600
                    send_serial(com_port, baud_num, data, self.log)
                time.sleep(0.5)
            self.log("✅ Test terminé\n")

        threading.Thread(target=worker, daemon=True).start()

    def _run_check_port(self):
        """Vérifie si un port est ouvert"""
        host = self.check_host_var.get().strip() or "127.0.0.1"
        try:
            port = int(self.check_port_var.get().strip())
        except:
            port = 40000

        threading.Thread(target=lambda: check_tcp_port(host, port, self.log),
                         daemon=True).start()

    def _run_show_wifi_passwords(self):
        """Récupère les mots de passe WiFi"""
        threading.Thread(target=lambda: get_wifi_passwords(self.log),
                         daemon=True).start()

    def _run_apply_wallpaper(self):
        """Applique le wallpaper sélectionné"""
        wallpaper = self.selected_wallpaper_var.get()
        if wallpaper:
            threading.Thread(
                target=lambda: apply_wallpaper(wallpaper, self.log),
                daemon=True).start()
        else:
            self.log("❌ Aucun wallpaper sélectionné")

    def _run_tweak_taskbar(self):
        """Applique les tweaks de la barre des tâches"""
        threading.Thread(target=lambda: tweak_taskbar(self.log),
                         daemon=True).start()

    def _run_disable_notifications(self):
        """Désactive les notifications Windows"""
        threading.Thread(
            target=lambda: disable_windows_notifications(self.log),
            daemon=True).start()

    def _run_restore_menu(self):
        """Restaure le menu contextuel classique"""
        threading.Thread(target=lambda: restore_context_menu(self.log),
                         daemon=True).start()

    def _run_uninstall_kb(self):
        """Désinstalle KB5064081"""
        threading.Thread(target=lambda: uninstall_kb5064081(self.log),
                         daemon=True).start()

    def _run_rename_pc(self):
        """Renomme le PC"""
        new_name = self.pc_name_var.get().strip()
        threading.Thread(target=lambda: rename_computer(new_name, self.log),
                         daemon=True).start()

    def _run_activate_windows(self, cmd):
        """Active Windows via PowerShell"""

        def worker():
            self.log(f"▶ Exécution PowerShell: {cmd}")
            try:
                import subprocess
                proc = subprocess.run([
                    "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                    "-Command", cmd
                ],
                                      capture_output=True,
                                      text=True,
                                      timeout=300)
                if proc.stdout:
                    self.log("----- PowerShell stdout -----")
                    for line in proc.stdout.splitlines():
                        self.log(line)
                if proc.stderr:
                    self.log("----- PowerShell stderr -----")
                    for line in proc.stderr.splitlines():
                        self.log(line)
                self.log(f"PowerShell terminé (code {proc.returncode})")
            except Exception as e:
                self.log(f"❌ Erreur: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def _show_system_info(self):
        """Affiche les informations système"""
        import platform
        import socket
        import getpass
        try:
            import psutil

            # Informations de base
            hostname = socket.gethostname()
            user = getpass.getuser()
            system = platform.system()
            release = platform.release()
            version = platform.version()

            # Processeur
            processor = platform.processor()
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            cpu_usage = psutil.cpu_percent(interval=1)

            # Nom du CPU (Intel i7-9600K, AMD Ryzen 5600X, etc.)
            cpu_name = "Non disponible"
            try:
                cpu_info_proc = subprocess.run('wmic cpu get name',
                                               shell=True,
                                               capture_output=True,
                                               text=True,
                                               timeout=5)
                if cpu_info_proc.returncode == 0 and cpu_info_proc.stdout:
                    lines = cpu_info_proc.stdout.strip().split('\n')
                    if len(lines) > 1:
                        cpu_name = lines[1].strip()
            except:
                pass

            # Mémoire RAM
            ram = psutil.virtual_memory()
            ram_total = round(ram.total / (1024**3), 2)
            ram_used = round(ram.used / (1024**3), 2)
            ram_percent = ram.percent

            # Type et fréquence de la RAM (DDR3/DDR4 + MHz)
            ram_type = "Non disponible"
            ram_speed = "Non disponible"
            try:
                # Type de RAM (DDR3, DDR4, DDR5)
                ram_type_proc = subprocess.run(
                    'wmic memorychip get memorytype',
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5)
                if ram_type_proc.returncode == 0 and ram_type_proc.stdout:
                    lines = [
                        l.strip()
                        for l in ram_type_proc.stdout.strip().split('\n')
                        if l.strip() and l.strip() != 'MemoryType'
                    ]
                    if lines:
                        # Codes: 20=DDR, 21=DDR2, 24=DDR3, 26=DDR4, 34=DDR5
                        type_code = lines[0].strip()
                        type_map = {
                            '20': 'DDR',
                            '21': 'DDR2',
                            '24': 'DDR3',
                            '26': 'DDR4',
                            '34': 'DDR5'
                        }
                        ram_type = type_map.get(type_code, f'Type {type_code}')

                # Fréquence de la RAM (MHz)
                ram_speed_proc = subprocess.run('wmic memorychip get speed',
                                                shell=True,
                                                capture_output=True,
                                                text=True,
                                                timeout=5)
                if ram_speed_proc.returncode == 0 and ram_speed_proc.stdout:
                    lines = [
                        l.strip()
                        for l in ram_speed_proc.stdout.strip().split('\n')
                        if l.strip() and l.strip() != 'Speed'
                    ]
                    if lines:
                        ram_speed = f"{lines[0].strip()} MHz"
            except:
                pass

            # Disques
            partitions = psutil.disk_partitions()

            self.log("=" * 60)
            self.log("                INFORMATIONS SYSTÈME")
            self.log("=" * 60)

            self.log("\n📋 SYSTÈME:")
            self.log(f"  Nom de l'ordinateur : {hostname}")
            self.log(f"  Utilisateur         : {user}")
            self.log(f"  OS                  : {system} {release}")
            self.log(f"  Version             : {version}")

            self.log("\n🔧 PROCESSEUR:")
            self.log(f"  Nom / Modèle        : {cpu_name}")
            self.log(f"  Détails             : {processor}")
            self.log(f"  Cœurs physiques     : {cpu_count_physical}")
            self.log(f"  Cœurs logiques      : {cpu_count_logical}")
            if cpu_freq:
                self.log(
                    f"  Fréquence           : {cpu_freq.current:.0f} MHz (max: {cpu_freq.max:.0f} MHz)"
                )
            self.log(f"  Utilisation actuelle: {cpu_usage}%")

            self.log("\n💾 MÉMOIRE RAM:")
            self.log(f"  Type                : {ram_type}")
            self.log(f"  Fréquence           : {ram_speed}")
            self.log(f"  Total               : {ram_total} GB")
            self.log(f"  Utilisée            : {ram_used} GB ({ram_percent}%)")
            self.log(
                f"  Disponible          : {round(ram.available / (1024**3), 2)} GB"
            )

            self.log("\n💿 DISQUES:")
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    total = round(usage.total / (1024**3), 2)
                    used = round(usage.used / (1024**3), 2)
                    free = round(usage.free / (1024**3), 2)
                    percent = usage.percent

                    self.log(f"  {partition.device}")
                    self.log(f"    Point de montage  : {partition.mountpoint}")
                    self.log(f"    Système de fichiers: {partition.fstype}")
                    self.log(f"    Taille totale     : {total} GB")
                    self.log(f"    Espace utilisé    : {used} GB ({percent}%)")
                    self.log(f"    Espace libre      : {free} GB")
                except Exception:
                    # Ignorer les lecteurs non accessibles
                    pass

            self.log("\n" + "=" * 60)

        except Exception as e:
            self.log(
                f"❌ Erreur lors de la récupération des infos système: {e}")

    def _run_create_shortcuts(self):
        """Crée les raccourcis VELBO/VELSRV"""
        folder = self.shortcut_folder_var.get().strip()
        threading.Thread(
            target=lambda: create_veloce_shortcuts(folder, self.log),
            daemon=True).start()

    def _build_manage_users_options(self, parent):
        """Page de gestion des utilisateurs Windows"""
        f = ctk.CTkScrollableFrame(parent)
        f.pack(fill="both", expand=True, padx=6, pady=6)

        ctk.CTkLabel(f,
                     text="Gestion des utilisateurs Windows",
                     font=ctk.CTkFont(size=16,
                                      weight="bold")).pack(anchor="w",
                                                           pady=(0, 10))

        # Variables
        if not hasattr(self, 'user_name_var'):
            self.user_name_var = tk.StringVar(value="")
            self.user_pass_var = tk.StringVar(value="")
            self.user_admin_var = tk.BooleanVar(value=False)

        # Formulaire création utilisateur
        form_frame = ctk.CTkFrame(f)
        form_frame.pack(fill="x", pady=8, padx=10)

        ctk.CTkLabel(form_frame, text="Nom d'utilisateur:").grid(row=0,
                                                                 column=0,
                                                                 sticky="w",
                                                                 padx=10,
                                                                 pady=5)
        ctk.CTkEntry(form_frame, textvariable=self.user_name_var,
                     width=250).grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="Mot de passe:").grid(row=1,
                                                            column=0,
                                                            sticky="w",
                                                            padx=10,
                                                            pady=5)
        ctk.CTkEntry(form_frame,
                     textvariable=self.user_pass_var,
                     width=250,
                     show="*").grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkCheckBox(form_frame,
                        text="Ajouter aux administrateurs",
                        variable=self.user_admin_var).grid(row=2,
                                                           column=0,
                                                           columnspan=2,
                                                           sticky="w",
                                                           padx=10,
                                                           pady=5)

        ctk.CTkButton(form_frame,
                      text="➕ Créer l'utilisateur",
                      width=200,
                      command=self._create_user,
                      fg_color="#2b6ee6",
                      hover_color="#2058c9").grid(row=3,
                                                  column=0,
                                                  columnspan=2,
                                                  pady=10)

        # Boutons presets
        preset_frame = ctk.CTkFrame(f)
        preset_frame.pack(fill="x", pady=8, padx=10)

        ctk.CTkLabel(preset_frame,
                     text="⚡ Presets rapides:",
                     font=ctk.CTkFont(size=13,
                                      weight="bold")).pack(anchor="w",
                                                           padx=10,
                                                           pady=(10, 5))

        btn_grid = ctk.CTkFrame(preset_frame, fg_color="transparent")
        btn_grid.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(btn_grid,
                      text="admin / veloce123",
                      width=150,
                      command=lambda:
                      (self.user_name_var.set("admin"),
                       self.user_pass_var.set("veloce123"),
                       self.user_admin_var.set(True))).grid(row=0,
                                                            column=0,
                                                            padx=5,
                                                            pady=5)

        ctk.CTkButton(btn_grid,
                      text="kpitech / Log1tech",
                      width=150,
                      command=lambda:
                      (self.user_name_var.set("kpitech"),
                       self.user_pass_var.set("Log1tech"),
                       self.user_admin_var.set(True))).grid(row=0,
                                                            column=1,
                                                            padx=5,
                                                            pady=5)

        # Bouton lister les utilisateurs
        ctk.CTkButton(f,
                      text="📋 Afficher tous les utilisateurs",
                      width=250,
                      command=self._list_users,
                      fg_color="#16a34a",
                      hover_color="#15803d").pack(pady=10)

        # === SECTION AUTO-LOGIN ===
        autologin_frame = ctk.CTkFrame(f, fg_color="#2b2b2b")
        autologin_frame.pack(fill="x", pady=15, padx=10)

        ctk.CTkLabel(autologin_frame,
                     text="🔐 Connexion automatique Windows",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w",
                                                                    padx=10,
                                                                    pady=(10, 5))

        # Afficher l'utilisateur auto-login actuel
        self.autologin_status_label = ctk.CTkLabel(autologin_frame,
                                                   text="⏳ Chargement...",
                                                   font=ctk.CTkFont(size=11))
        self.autologin_status_label.pack(anchor="w", padx=10, pady=(0, 5))

        # Bouton pour vérifier l'utilisateur auto-login
        ctk.CTkButton(autologin_frame,
                      text="🔍 Vérifier utilisateur auto-login",
                      width=220,
                      command=self._check_autologin,
                      fg_color="#0284c7",
                      hover_color="#0369a1").pack(anchor="w", padx=10, pady=5)

        # Formulaire pour configurer l'auto-login
        config_frame = ctk.CTkFrame(autologin_frame, fg_color="#1f2937")
        config_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(config_frame,
                     text="Configurer la connexion automatique:",
                     font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0,
                                                                    columnspan=2,
                                                                    sticky="w",
                                                                    padx=10,
                                                                    pady=(8, 5))

        if not hasattr(self, 'autologin_user_var'):
            self.autologin_user_var = tk.StringVar(value="")
            self.autologin_pass_var = tk.StringVar(value="")

        ctk.CTkLabel(config_frame, text="Utilisateur:").grid(row=1, column=0,
                                                             sticky="w",
                                                             padx=10, pady=5)
        ctk.CTkEntry(config_frame,
                     textvariable=self.autologin_user_var,
                     width=200).grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(config_frame, text="Mot de passe:").grid(row=2, column=0,
                                                              sticky="w",
                                                              padx=10, pady=5)
        ctk.CTkEntry(config_frame,
                     textvariable=self.autologin_pass_var,
                     width=200,
                     show="*").grid(row=2, column=1, padx=10, pady=5)

        btn_row = ctk.CTkFrame(config_frame, fg_color="transparent")
        btn_row.grid(row=3, column=0, columnspan=2, pady=8)

        ctk.CTkButton(btn_row,
                      text="✅ Activer auto-login",
                      width=140,
                      command=self._enable_autologin,
                      fg_color="#16a34a",
                      hover_color="#15803d").pack(side="left", padx=5)

        ctk.CTkButton(btn_row,
                      text="❌ Désactiver auto-login",
                      width=140,
                      command=self._disable_autologin,
                      fg_color="#dc2626",
                      hover_color="#b91c1c").pack(side="left", padx=5)

    def _create_user(self):
        """Crée un nouvel utilisateur Windows"""
        name = self.user_name_var.get().strip()
        password = self.user_pass_var.get().strip()
        is_admin = self.user_admin_var.get()

        if not name or not password:
            self.log("❌ Nom d'utilisateur et mot de passe requis")
            return

        threading.Thread(target=lambda: add_windows_user(
            name, password, is_admin, True, self.log),
                         daemon=True).start()

    def _list_users(self):
        """Liste tous les utilisateurs Windows"""

        def worker():
            try:
                self.log("===== UTILISATEURS WINDOWS =====")
                result = subprocess.check_output("net user",
                                                 shell=True,
                                                 text=True)
                for line in result.splitlines():
                    if line.strip():
                        self.log(line)
                self.log("================================")
            except Exception as e:
                self.log(f"❌ Erreur: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def _check_autologin(self):
        """Vérifie l'utilisateur configuré pour l'auto-login"""
        def worker():
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
                                    0, winreg.KEY_READ)

                try:
                    auto_enabled, _ = winreg.QueryValueEx(key, "AutoAdminLogon")
                    username, _ = winreg.QueryValueEx(key, "DefaultUserName")

                    if auto_enabled == "1":
                        status_text = f"✅ Auto-login ACTIVÉ pour: {username}"
                        color = "#10b981"
                        self.autologin_user_var.set(username)
                        self.log(f"ℹ️ Auto-login activé pour l'utilisateur: {username}")
                    else:
                        status_text = "⚠️ Auto-login DÉSACTIVÉ"
                        color = "#f59e0b"
                        self.log("ℹ️ Auto-login désactivé")
                except:
                    status_text = "⚠️ Auto-login DÉSACTIVÉ (non configuré)"
                    color = "#f59e0b"
                    self.log("ℹ️ Auto-login non configuré")

                winreg.CloseKey(key)

            except Exception as e:
                status_text = f"❌ Erreur: {e}"
                color = "#ef4444"
                self.log(f"❌ Erreur vérification auto-login: {e}")

            # Mettre à jour le label dans le thread principal
            self.after(0, lambda: self.autologin_status_label.configure(
                text=status_text, text_color=color))

        threading.Thread(target=worker, daemon=True).start()

    def _enable_autologin(self):
        """Active l'auto-login Windows"""
        username = self.autologin_user_var.get().strip()
        password = self.autologin_pass_var.get().strip()

        if not username:
            self.log("❌ Nom d'utilisateur requis")
            return

        def worker():
            try:
                import winreg
                self.log(f"▶ Configuration auto-login pour: {username}")

                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
                                    0, winreg.KEY_SET_VALUE)

                winreg.SetValueEx(key, "AutoAdminLogon", 0, winreg.REG_SZ, "1")
                winreg.SetValueEx(key, "DefaultUserName", 0, winreg.REG_SZ, username)
                if password:
                    winreg.SetValueEx(key, "DefaultPassword", 0, winreg.REG_SZ, password)

                winreg.CloseKey(key)

                self.log(f"✅ Auto-login activé pour: {username}")
                self.log("⚠️ L'utilisateur se connectera automatiquement au prochain démarrage")

                # Mettre à jour le statut
                self.after(0, lambda: self.autologin_status_label.configure(
                    text=f"✅ Auto-login ACTIVÉ pour: {username}",
                    text_color="#10b981"))

            except Exception as e:
                self.log(f"❌ Erreur activation auto-login: {e}")
                self.log("⚠️ Nécessite les droits administrateur")

        threading.Thread(target=worker, daemon=True).start()

    def _disable_autologin(self):
        """Désactive l'auto-login Windows"""
        def worker():
            try:
                import winreg
                self.log("▶ Désactivation de l'auto-login...")

                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
                                    0, winreg.KEY_SET_VALUE)

                winreg.SetValueEx(key, "AutoAdminLogon", 0, winreg.REG_SZ, "0")

                # Optionnel: supprimer le mot de passe stocké
                try:
                    winreg.DeleteValue(key, "DefaultPassword")
                except:
                    pass

                winreg.CloseKey(key)

                self.log("✅ Auto-login désactivé")
                self.log("ℹ️ Windows demandera un mot de passe au prochain démarrage")

                # Mettre à jour le statut
                self.after(0, lambda: self.autologin_status_label.configure(
                    text="⚠️ Auto-login DÉSACTIVÉ",
                    text_color="#f59e0b"))

            except Exception as e:
                self.log(f"❌ Erreur désactivation auto-login: {e}")
                self.log("⚠️ Nécessite les droits administrateur")

        threading.Thread(target=worker, daemon=True).start()

    def _update_remote_ids(self):
        """Met à jour les IDs TeamViewer et AnyDesk"""
        tv_id = get_teamviewer_id()
        ad_id = get_anydesk_id()
        self.after(
            0, lambda: self.tv_label.configure(text=f"TeamViewer ID: {tv_id}"))
        self.after(
            0, lambda: self.ad_label.configure(text=f"AnyDesk ID: {ad_id}"))

    def show_release_notes(self):
        """Affiche les notes de version dans une fenêtre popup"""
        from tkinter import Toplevel
        from tkinter import scrolledtext

        base_path = get_base_path()
        notes_path = os.path.join(base_path, "config", "releasesnotes.txt")

        if not os.path.exists(notes_path):
            self.log(f"❌ Fichier releasesnotes.txt introuvable dans config/")
            messagebox.showwarning(
                "Fichier introuvable",
                "Le fichier releasesnotes.txt est manquant dans config/")
            return

        win = Toplevel(self)
        win.title("Release Notes - Outils Système")
        win.geometry("700x500")
        win.resizable(True, True)
        win.grab_set()

        txt_area = scrolledtext.ScrolledText(win,
                                             wrap="word",
                                             font=("Consolas", 11))
        txt_area.pack(expand=True, fill="both", padx=10, pady=10)

        try:
            with open(notes_path, "r", encoding="utf-8") as f:
                txt_area.insert("1.0", f.read())
        except Exception as e:
            txt_area.insert("1.0",
                            f"Erreur lors de la lecture du fichier: {e}")

        txt_area.configure(state="disabled")

    def build_auto_setup_options(self, parent):
        """Page Auto Setup avec 3 boutons qui ouvrent des fenêtres dédiées"""
        f = ctk.CTkScrollableFrame(parent)
        f.pack(fill="both", expand=True, padx=6, pady=6)

        # Titre
        ctk.CTkLabel(f,
                     text="Auto Setup - Configuration automatique",
                     font=ctk.CTkFont(size=18,
                                      weight="bold")).pack(anchor="w",
                                                           pady=(0, 15))

        ctk.CTkLabel(f,
                     text="Sélectionnez le type de poste à configurer :",
                     font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 10))

        # Boutons pour ouvrir chaque fenêtre
        btn_frame = ctk.CTkFrame(f, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        ctk.CTkButton(btn_frame,
                      text="🖥️ Config PC",
                      width=220,
                      height=60,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      fg_color="#16a34a",
                      hover_color="#15803d",
                      command=self._open_config_pc_window).grid(row=0,
                                                                column=0,
                                                                padx=15,
                                                                pady=10)

        ctk.CTkButton(btn_frame,
                      text="💳 Station Veloce",
                      width=220,
                      height=60,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      fg_color="#2563eb",
                      hover_color="#1d4ed8",
                      command=self._open_veloce_window).grid(row=0,
                                                             column=2,
                                                             padx=15,
                                                             pady=10)

        # Descriptions
        desc_frame = ctk.CTkFrame(f)
        desc_frame.pack(fill="both", expand=True, pady=(15, 0))

        ctk.CTkLabel(desc_frame,
                     text="📋 Description des configurations :",
                     font=ctk.CTkFont(size=13,
                                      weight="bold")).pack(anchor="w",
                                                           padx=15,
                                                           pady=(15, 10))

        descriptions = """
• Config PC:
  - Poste Standard: Tweaks Windows, utilisateurs, wallpaper
  - Poste Serveur: Raccourcis VELBO/VELSRV, partage c:\\veloce

• Station Veloce:
  - Installation automatique réseau
  - Configuration POS complète
"""

        ctk.CTkLabel(desc_frame,
                     text=descriptions,
                     justify="left",
                     font=ctk.CTkFont(size=11)).pack(anchor="w",
                                                     padx=25,
                                                     pady=(0, 15))

    def _check_veloce_share_status(self):
        """Vérifie si le dossier c:\\veloce existe et est partagé"""
        veloce_path = r"c:\veloce"
        exists = os.path.exists(veloce_path)
        shared = False

        if exists:
            try:
                # Vérifier si le dossier est partagé via WMI
                result = subprocess.run(
                    'wmic share where "path=\'c:\\\\veloce\'" get name',
                    capture_output=True,
                    text=True,
                    shell=True,
                    timeout=5)
                shared = "veloce" in result.stdout.lower()
            except:
                pass

        return exists, shared

    def _check_password_protected_sharing(self):
        """Vérifie si le partage protégé par mot de passe est activé"""
        try:
            import winreg
            # Vérifier la clé everyoneincludesanonymous
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SYSTEM\CurrentControlSet\Control\Lsa", 0,
                                 winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "everyoneincludesanonymous")
            winreg.CloseKey(key)

            # Si everyoneincludesanonymous = 1, le partage protégé est désactivé
            # Si = 0 ou absent, le partage protégé est activé
            return value == 0
        except:
            # Par défaut, considérer que le partage protégé est activé
            return True

    def _disable_password_protected_sharing(self, log_fn):
        """Désactive le partage protégé par mot de passe"""
        try:
            import winreg

            log_fn("▶ Désactivation du partage protégé par mot de passe...")

            # Étape 1: Modifier everyoneincludesanonymous
            key1 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                  r"SYSTEM\CurrentControlSet\Control\Lsa", 0,
                                  winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key1, "everyoneincludesanonymous", 0,
                              winreg.REG_DWORD, 1)
            winreg.CloseKey(key1)
            log_fn("✓ Clé 'everyoneincludesanonymous' définie à 1")

            # Étape 2: Modifier RestrictNullSessAccess
            key2 = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters",
                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key2, "RestrictNullSessAccess", 0,
                              winreg.REG_DWORD, 0)
            winreg.CloseKey(key2)
            log_fn("✓ Clé 'RestrictNullSessAccess' définie à 0")

            ########

            key3 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                  r"SYSTEM\CurrentControlSet\Control\Lsa", 0,
                                  winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key3, "ForceGuest", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key3)
            log_fn("✓ Clé 'ForceGuest' définie à 0 (désactivé)")
            ####

            key4 = winreg.CreateKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System")
            winreg.SetValueEx(key4, "LocalAccountTokenFilterPolicy", 0,
                              winreg.REG_DWORD, 1)
            winreg.CloseKey(key4)
            log_fn(
                "✓ Clé 'LocalAccountTokenFilterPolicy' définie à 1 (désactivé)"
            )

            log_fn("✅ Partage protégé par mot de passe désactivé")
            log_fn(
                "⚠️ Redémarrage ou déconnexion/reconnexion du réseau requis pour appliquer"
            )

        except Exception as e:
            log_fn(f"❌ Erreur désactivation partage protégé: {e}")
            log_fn("⚠️ Nécessite droits administrateur")

    def _enable_password_protected_sharing(self, log_fn):
        """Active le partage protégé par mot de passe"""
        try:
            import winreg

            log_fn("▶ Activation du partage protégé par mot de passe...")

            # Étape 1: Modifier everyoneincludesanonymous
            key1 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                  r"SYSTEM\CurrentControlSet\Control\Lsa", 0,
                                  winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key1, "everyoneincludesanonymous", 0,
                              winreg.REG_DWORD, 0)
            winreg.CloseKey(key1)
            log_fn("✓ Clé 'everyoneincludesanonymous' définie à 0")

            # Étape 2: Modifier RestrictNullSessAccess
            key2 = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters",
                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key2, "RestrictNullSessAccess", 0,
                              winreg.REG_DWORD, 1)
            winreg.CloseKey(key2)
            log_fn("✓ Clé 'RestrictNullSessAccess' définie à 1")

            #####

            key3 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                  r"SYSTEM\CurrentControlSet\Control\Lsa", 0,
                                  winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key3, "ForceGuest", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key3)
            log_fn("✓ Clé 'ForceGuest' définie à 1 (activé)")

            ####

            key4 = winreg.CreateKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System")
            winreg.SetValueEx(key4, "LocalAccountTokenFilterPolicy", 0,
                              winreg.REG_DWORD, 0)
            winreg.CloseKey(key4)
            log_fn(
                "✓ Clé 'LocalAccountTokenFilterPolicy' définie à 0 (activé)")

            log_fn("✅ Partage protégé par mot de passe activé")
            log_fn(
                "⚠️ Redémarrage ou déconnexion/reconnexion du réseau requis pour appliquer"
            )

        except Exception as e:
            log_fn(f"❌ Erreur activation partage protégé: {e}")
            log_fn("⚠️ Nécessite droits administrateur")

    # === NOUVELLES FONCTIONS POUR OPTIONS 1-8 ===

    def _disable_uac(self, log_fn):
        """Option 1: Désactiver le contrôle de compte utilisateur (UAC)"""
        try:
            import winreg

            log_fn("▶ Désactivation du contrôle de compte utilisateur (UAC)...")

            # Modifier la clé de registre pour UAC
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "EnableLUA", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "ConsentPromptBehaviorAdmin", 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, "PromptOnSecureDesktop", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)

            log_fn("✓ Clés UAC modifiées (EnableLUA=0, ConsentPromptBehaviorAdmin=0)")
            log_fn("✅ UAC désactivé")
            log_fn("⚠️ Redémarrage requis pour appliquer les changements")

        except Exception as e:
            log_fn(f"❌ Erreur désactivation UAC: {e}")
            log_fn("⚠️ Nécessite droits administrateur")

    def _allow_veloce_firewall(self, log_fn):
        """Option 2: Autoriser Veloce Backoffice dans le pare-feu"""
        try:
            log_fn("▶ Autorisation de Veloce Backoffice dans le pare-feu...")

            veloce_path = r"C:\Veloce\VelSrv\VelSrv.exe"

            # Vérifier si le fichier existe
            if not os.path.exists(veloce_path):
                log_fn(f"⚠️ Fichier non trouvé: {veloce_path}")
                log_fn("   Le pare-feu sera configuré mais l'application n'est pas installée")

            # Ajouter une règle de pare-feu pour Veloce Backoffice
            cmd = f'netsh advfirewall firewall add rule name="Veloce Backoffice" dir=in action=allow program="{veloce_path}" enable=yes profile=any'

            result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=30)

            if result.returncode == 0:
                log_fn("✓ Règle de pare-feu ajoutée pour Veloce Backoffice")
                log_fn("✅ Veloce Backoffice autorisé dans le pare-feu (Public & Privé)")
            else:
                # La règle existe peut-être déjà, essayer de la mettre à jour
                log_fn("  Règle existante détectée, tentative de mise à jour...")
                cmd_update = f'netsh advfirewall firewall set rule name="Veloce Backoffice" new enable=yes profile=any'
                result_update = subprocess.run(cmd_update, capture_output=True, text=True, shell=True, timeout=30)

                if result_update.returncode == 0:
                    log_fn("✓ Règle de pare-feu mise à jour pour Veloce Backoffice")
                    log_fn("✅ Veloce Backoffice autorisé dans le pare-feu (Public & Privé)")
                else:
                    log_fn("❌ Échec de la configuration du pare-feu")
                    log_fn(f"   Erreur: {result_update.stderr.strip()}")
                    log_fn("⚠️ Nécessite droits administrateur")

        except Exception as e:
            log_fn(f"❌ Erreur configuration pare-feu: {e}")
            log_fn("⚠️ Nécessite droits administrateur")

    def _disable_network_sleep(self, log_fn):
        """Option 3: Désactiver la mise en veille des cartes réseau"""
        try:
            log_fn("▶ Désactivation de la mise en veille des cartes réseau...")

            # Utiliser PowerShell pour modifier les paramètres des adaptateurs réseau
            ps_cmd = '''
Get-NetAdapter | ForEach-Object {
    $adapter = $_
    $powerMgmt = Get-WmiObject MSPower_DeviceEnable -Namespace root\\wmi | Where-Object {$_.InstanceName -match [regex]::Escape($adapter.PnPDeviceID)}
    if ($powerMgmt) {
        $powerMgmt.Enable = $false
        $powerMgmt.Put()
        Write-Output "Désactivé pour: $($adapter.Name)"
    }
}
'''

            result = subprocess.run(['powershell', '-Command', ps_cmd],
                                   capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if line.strip():
                        log_fn(f"  ✓ {line.strip()}")
                log_fn("✅ Mise en veille des cartes réseau désactivée")
            else:
                log_fn("⚠️ Impossible de modifier certaines cartes réseau")
                log_fn("   Essai avec méthode alternative...")

                # Méthode alternative via netsh
                subprocess.run('powercfg /change standby-timeout-ac 0', shell=True, timeout=10)
                subprocess.run('powercfg /change standby-timeout-dc 0', shell=True, timeout=10)
                log_fn("✓ Paramètres d'alimentation réseau modifiés")

        except Exception as e:
            log_fn(f"❌ Erreur désactivation veille réseau: {e}")
            log_fn("⚠️ Nécessite droits administrateur")

    def _set_timezone_and_sync(self, log_fn):
        """Option 4: Configurer fuseau horaire America/Toronto et synchroniser"""
        try:
            log_fn("▶ Configuration du fuseau horaire et synchronisation...")

            # Définir le fuseau horaire sur America/Toronto (Eastern Time)
            cmd_tz = 'tzutil /s "Eastern Standard Time"'
            result = subprocess.run(cmd_tz, capture_output=True, text=True, shell=True, timeout=10)

            if result.returncode == 0:
                log_fn("✓ Fuseau horaire défini sur America/Toronto (Eastern)")
            else:
                log_fn("⚠️ Erreur lors du changement de fuseau horaire")

            # Forcer la synchronisation de l'heure
            log_fn("  Synchronisation de l'heure en cours...")

            # Arrêter le service W32Time
            subprocess.run('net stop w32time', capture_output=True, shell=True, timeout=10)

            # Configurer le service pour démarrer automatiquement
            subprocess.run('sc config w32time start= auto', capture_output=True, shell=True, timeout=10)
            log_fn("✓ Service de temps configuré en démarrage automatique")

            # Redémarrer le service W32Time
            subprocess.run('net start w32time', capture_output=True, shell=True, timeout=10)
            log_fn("✓ Service de temps redémarré")

            # Enregistrer le service avec le serveur de temps
            subprocess.run('w32tm /register', capture_output=True, shell=True, timeout=10)

            # Configurer les serveurs de temps NTP
            time_servers = 'time.windows.com,time.nist.gov,pool.ntp.org'
            subprocess.run(f'w32tm /config /manualpeerlist:"{time_servers}" /syncfromflags:manual /reliable:YES /update',
                          capture_output=True, shell=True, timeout=15)
            log_fn("✓ Serveurs de temps NTP configurés")

            # Forcer la resynchronisation immédiate
            result_sync = subprocess.run('w32tm /resync /force',
                                        capture_output=True, text=True, shell=True, timeout=30)

            if "successfully" in result_sync.stdout.lower() or result_sync.returncode == 0:
                log_fn("✓ Heure synchronisée avec succès")
            else:
                log_fn("⚠️ La synchronisation peut prendre quelques instants")

            # Activer la synchronisation automatique
            subprocess.run('w32tm /config /update', capture_output=True, shell=True, timeout=10)
            log_fn("✓ Synchronisation automatique activée")

            log_fn("✅ Fuseau horaire et synchronisation configurés")

        except Exception as e:
            log_fn(f"❌ Erreur configuration fuseau horaire: {e}")

    def _set_network_private(self, log_fn):
        """Option 3b: Mettre la carte réseau en mode Privé (au lieu de Public)"""
        try:
            log_fn("▶ Configuration carte réseau en mode Privé...")

            # PowerShell pour définir toutes les cartes réseau en mode Privé
            ps_cmd = 'Get-NetConnectionProfile | Set-NetConnectionProfile -NetworkCategory Private'

            result = subprocess.run(['powershell', '-Command', ps_cmd],
                                  capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                log_fn("✓ Carte(s) réseau configurée(s) en mode Privé")
                log_fn("✅ Configuration réseau Privé terminée")
            else:
                log_fn(f"⚠️ Résultat de la commande: {result.stderr.strip() if result.stderr else 'OK'}")
                log_fn("✓ Commande exécutée (vérifier manuellement si nécessaire)")

        except Exception as e:
            log_fn(f"❌ Erreur configuration réseau Privé: {e}")
            log_fn("⚠️ Configuration manuelle requise:")
            log_fn("   Paramètres → Réseau → Propriétés → Profil réseau → Privé")

    def _set_best_performance(self, log_fn):
        """Option 5: Configurer les meilleures performances système"""
        try:
            import winreg

            log_fn("▶ Configuration des meilleures performances système...")

            # Modifier la clé de registre pour les performances visuelles
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)  # 2 = Best Performance
            winreg.CloseKey(key)

            log_fn("✓ Paramètres de performances visuelles modifiés")

            # Désactiver les animations
            key2 = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Control Panel\Desktop\WindowMetrics",
                                 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key2, "MinAnimate", 0, winreg.REG_SZ, "0")
            winreg.CloseKey(key2)

            log_fn("✓ Animations désactivées")
            log_fn("✅ Meilleures performances configurées")
            log_fn("⚠️ Redémarrage ou déconnexion/reconnexion recommandé")

        except Exception as e:
            log_fn(f"❌ Erreur configuration performances: {e}")

    def _set_power_performance(self, log_fn):
        """Option 6: Configurer le mode d'alimentation performance"""
        try:
            log_fn("▶ Configuration du mode d'alimentation performance...")

            # Définir le mode de performance élevée
            cmd_power = 'powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'  # GUID du mode Performance élevée
            subprocess.run(cmd_power, capture_output=True, shell=True, timeout=10)
            log_fn("✓ Mode alimentation 'Performance élevée' activé")

            # Désactiver la mise en veille
            subprocess.run('powercfg /change standby-timeout-ac 0', shell=True, timeout=10)
            subprocess.run('powercfg /change standby-timeout-dc 0', shell=True, timeout=10)
            log_fn("✓ Mise en veille désactivée")

            # Jamais éteindre l'écran
            subprocess.run('powercfg /change monitor-timeout-ac 0', shell=True, timeout=10)
            subprocess.run('powercfg /change monitor-timeout-dc 0', shell=True, timeout=10)
            log_fn("✓ Extinction automatique de l'écran désactivée")

            # Arrêt du disque dur = 0
            subprocess.run('powercfg /change disk-timeout-ac 0', shell=True, timeout=10)
            subprocess.run('powercfg /change disk-timeout-dc 0', shell=True, timeout=10)
            log_fn("✓ Arrêt automatique du disque dur désactivé")

            log_fn("✅ Mode alimentation performance configuré")

        except Exception as e:
            log_fn(f"❌ Erreur configuration alimentation: {e}")

    def _install_ninite(self, log_fn):
        """Option 9: Installer Ninite (Notepad++, 7zip, Foxit, TightVNC)"""
        try:
            log_fn("▶ Installation de Ninite en cours...")

            # Chemin vers ninite.exe
            ninite_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'installers', 'ninite.exe')
            ninite_path = os.path.abspath(ninite_path)

            if not os.path.exists(ninite_path):
                log_fn("❌ Fichier ninite.exe non trouvé dans assets/installers/")
                log_fn("   Veuillez placer ninite.exe dans le dossier assets/installers/")
                return

            log_fn(f"✓ Fichier ninite.exe trouvé: {ninite_path}")
            log_fn("  Lancement de l'installation...")
            log_fn("  ⏳ Cela peut prendre plusieurs minutes (Notepad++, 7zip, Foxit, TightVNC)")
            log_fn("  ⏳ Veuillez patienter, ne pas fermer la fenêtre...")

            # Lancer ninite SANS paramètre (il est silencieux par défaut)
            # NE PAS CAPTURER stdout/stderr pour éviter le blocage des pipes
            try:
                # Utiliser CREATE_NO_WINDOW sur Windows pour exécution silencieuse
                creation_flags = 0x08000000 if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0

                result = subprocess.run([ninite_path],
                                       timeout=600,
                                       creationflags=creation_flags)

                if result.returncode == 0:
                    log_fn("✓ Installation de Ninite terminée avec succès")
                else:
                    log_fn(f"✓ Installation terminée (code retour: {result.returncode})")

                # Attendre et configurer le mot de passe VNC TightVNC
                log_fn("")
                log_fn("  Configuration du mot de passe VNC en cours...")
                self._configure_vnc_password(log_fn)

            except subprocess.TimeoutExpired:
                log_fn("⚠️ Installation prend plus de 10 minutes")
                log_fn("   L'installation continue probablement en arrière-plan")
                log_fn("   Configurez le mot de passe VNC manuellement plus tard")

            log_fn("✅ Processus Ninite terminé")

        except Exception as e:
            log_fn(f"❌ Erreur installation Ninite: {e}")
            log_fn("   Vérifiez que le fichier ninite.exe est correct")

    def _configure_vnc_password(self, log_fn):
        """Configurer le mot de passe VNC TightVNC à Log1tech"""
        try:
            import time

            log_fn("▶ Configuration du mot de passe VNC...")
            log_fn("  Attente de l'installation de TightVNC...")

            # Chemins possibles pour TightVNC
            vnc_paths = [
                r"C:\Program Files\TightVNC\tvnserver.exe",
                r"C:\Program Files (x86)\TightVNC\tvnserver.exe"
            ]

            # Attendre jusqu'à 60 secondes que TightVNC soit installé
            vnc_server_path = None
            max_wait = 60
            wait_interval = 5

            for attempt in range(max_wait // wait_interval):
                for path in vnc_paths:
                    if os.path.exists(path):
                        vnc_server_path = path
                        break

                if vnc_server_path:
                    break

                if attempt == 0:
                    log_fn(f"  Attente installation TightVNC... ({wait_interval * (attempt + 1)}s)")
                elif attempt < (max_wait // wait_interval) - 1:
                    log_fn(f"  Toujours en attente... ({wait_interval * (attempt + 1)}s)")

                time.sleep(wait_interval)

            if vnc_server_path:
                log_fn(f"✓ TightVNC Server détecté: {vnc_server_path}")

                # Attendre encore 3 secondes pour que l'installation se finalise
                time.sleep(3)

                # Configurer TightVNC pour démarrage automatique + mot de passe
                try:
                    import winreg

                    log_fn("  Configuration du service TightVNC...")

                    # Configurer le service pour démarrage automatique
                    subprocess.run('sc config tvnserver start= auto', 
                                  capture_output=True, shell=True, timeout=10)
                    log_fn("✓ Service TightVNC configuré pour démarrage automatique")

                    # Arrêter le service VNC s'il tourne
                    subprocess.run('net stop tvnserver', capture_output=True, shell=True, timeout=10)
                    time.sleep(1)

                    # Configurer via le registre avec les valeurs chiffrées
                    try:
                        # Ouvrir ou créer la clé TightVNC Server
                        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, 
                                              r"SOFTWARE\TightVNC\Server")

                        # Configurer les paramètres de base
                        winreg.SetValueEx(key, "AcceptRfbConnections", 0, winreg.REG_DWORD, 1)
                        winreg.SetValueEx(key, "LoopbackOnly", 0, winreg.REG_DWORD, 0)
                        winreg.SetValueEx(key, "AllowLoopback", 0, winreg.REG_DWORD, 1)
                        winreg.SetValueEx(key, "UseAuthentication", 0, winreg.REG_DWORD, 1)

                        # Mot de passe "Log1tech" chiffré en DES VNC (8 bytes)
                        # Valeurs hexadécimales du fichier .reg fourni par l'utilisateur
                        password_encrypted = bytes([0x5d, 0xd9, 0xd3, 0x3a, 0x0c, 0xed, 0x17, 0xdb])
                        control_password_encrypted = bytes([0x5d, 0xd9, 0xd3, 0x3a, 0x0c, 0xed, 0x17, 0xdb])

                        # Écrire les mots de passe chiffrés dans le registre
                        winreg.SetValueEx(key, "Password", 0, winreg.REG_BINARY, password_encrypted)
                        winreg.SetValueEx(key, "ControlPassword", 0, winreg.REG_BINARY, control_password_encrypted)

                        winreg.CloseKey(key)
                        log_fn("✓ Configuration registre TightVNC mise à jour")
                        log_fn("✓ Mots de passe chiffrés écrits dans le registre")

                    except Exception as reg_error:
                        log_fn(f"⚠️ Erreur configuration registre: {reg_error}")

                    # Redémarrer le service
                    result = subprocess.run('net start tvnserver', 
                                          capture_output=True, shell=True, timeout=10)

                    if result.returncode == 0:
                        log_fn("✓ Service TightVNC démarré")
                    else:
                        log_fn("⚠️ Démarrage du service (vérifier manuellement)")

                    log_fn("✅ Configuration VNC terminée")
                    log_fn("  ✓ Démarrage automatique: Activé")
                    log_fn("  ✓ Mot de passe: Log1tech (Primary Password)")
                    log_fn("")
                    log_fn("⚠️ Si le mot de passe ne fonctionne pas, configurez manuellement:")
                    log_fn("   1. Clic droit sur l'icône TightVNC (barre des tâches)")
                    log_fn("   2. Administration → Paramètres du serveur")
                    log_fn("   3. Onglet 'Authentification' → Primary Password")
                    log_fn("   4. Entrer: Log1tech")

                except Exception as e:
                    log_fn(f"⚠️ Configuration automatique échouée: {e}")
                    log_fn("   Configurez manuellement le service et mot de passe VNC")

            else:
                log_fn("⚠️ TightVNC Server non trouvé après 60 secondes")
                log_fn("   L'installation a peut-être échoué ou n'est pas terminée")
                log_fn("   Mot de passe recommandé: Log1tech (à configurer manuellement)")

        except Exception as e:
            log_fn(f"⚠️ Configuration VNC manuelle requise: {e}")
            log_fn("   Mot de passe recommandé: Log1tech")

    def _set_active_hours(self, log_fn, start_hour, end_hour):
        """Option 8: Configurer les heures actives du système"""
        try:
            import winreg

            log_fn(f"▶ Configuration des heures actives ({start_hour}h - {end_hour}h)...")

            # Valider les heures
            try:
                start = int(start_hour)
                end = int(end_hour)
                if start < 0 or start > 23 or end < 0 or end > 23:
                    log_fn("❌ Les heures doivent être entre 0 et 23")
                    return
                # Permettre les heures passant minuit (ex: 17h-5h est valide)
                # Pas de vérification start >= end
            except ValueError:
                log_fn("❌ Format d'heure invalide")
                return

            # Modifier la clé de registre pour les heures actives
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SOFTWARE\Microsoft\WindowsUpdate\UX\Settings",
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "ActiveHoursStart", 0, winreg.REG_DWORD, start)
            winreg.SetValueEx(key, "ActiveHoursEnd", 0, winreg.REG_DWORD, end)
            winreg.CloseKey(key)

            if start >= end:
                log_fn(f"✓ Heures actives définies: {start}h - {end}h (passant minuit)")
            else:
                log_fn(f"✓ Heures actives définies: {start}h - {end}h")
            log_fn("✅ Heures actives configurées")
            log_fn("   Windows ne redémarrera pas automatiquement pendant ces heures")

        except Exception as e:
            log_fn(f"❌ Erreur configuration heures actives: {e}")
            log_fn("⚠️ Nécessite droits administrateur")

    def _open_config_pc_window(self):
        """Ouvre la fenêtre Config PC avec 2 colonnes (Standard | Serveur)"""
        from tkinter import Toplevel

        # Créer la fenêtre
        window = Toplevel(self)
        window.title("Auto Setup - Config PC")
        window.geometry("1000x580")
        window.resizable(True, True)
        window.transient(self)
        window.grab_set()

        # Maximiser la fenêtre au chargement
        try:
            window.state('zoomed')  # Windows
        except:
            window.attributes('-zoomed', True)  # Linux

        # Frame principal
        main_frame = ctk.CTkFrame(window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Titre
        #ctk.CTkLabel(main_frame, text="🖥️ Config PC",
        #             font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0,6))

        # Container horizontal: 3 colonnes (Standard | Serveur+Options | Log)
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=(0, 6))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_columnconfigure(2, weight=1)

        # Variables
        standard_vars = {
            'taskbar': tk.BooleanVar(value=True),
            'notifications': tk.BooleanVar(value=True),
            'user_admin': tk.BooleanVar(value=True),
            'user_kpitech': tk.BooleanVar(value=True),
            'wallpaper': tk.BooleanVar(value=True),
        }
        serveur_vars = {
            'shortcuts': tk.BooleanVar(value=False),
            'share': tk.BooleanVar(value=False),
        }
        rename_var = tk.BooleanVar(value=False)
        current_pc_name = os.environ.get("COMPUTERNAME", "")
        pc_name_var = tk.StringVar(value=current_pc_name)
        restart_var = tk.BooleanVar(value=False)

        # === COLONNE 1: POSTE STANDARD ===
        col1 = ctk.CTkFrame(content_frame, fg_color="#2b2b2b")
        col1.grid(row=0, column=0, sticky="nsew", padx=(0, 3))

        ctk.CTkLabel(col1,
                     text="📋 Poste Standard",
                     font=ctk.CTkFont(size=12,
                                      weight="bold")).pack(pady=(6, 4))

        ctk.CTkCheckBox(col1,
                        text="✓ Tweak barre tâches",
                        variable=standard_vars['taskbar']).pack(anchor="w",
                                                                padx=8,
                                                                pady=1)
        ctk.CTkCheckBox(col1,
                        text="✓ Désactiver notif.",
                        variable=standard_vars['notifications']).pack(
                            anchor="w", padx=8, pady=1)
        ctk.CTkCheckBox(col1,
                        text="✓ User 'admin'",
                        variable=standard_vars['user_admin']).pack(anchor="w",
                                                                   padx=8,
                                                                   pady=1)
        ctk.CTkCheckBox(col1,
                        text="✓ User 'kpitech'",
                        variable=standard_vars['user_kpitech']).pack(
                            anchor="w", padx=8, pady=1)
        ctk.CTkCheckBox(col1,
                        text="✓ Wallpaper KPI",
                        variable=standard_vars['wallpaper']).pack(anchor="w",
                                                                  padx=8,
                                                                  pady=1)

        # === NOUVELLES OPTIONS ===

        # Option 1: Désactiver UAC (cochée par défaut)
        standard_vars['disable_uac'] = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(col1,
                        text="✓ Désactiver UAC",
                        variable=standard_vars['disable_uac']).pack(anchor="w",
                                                                   padx=8,
                                                                   pady=1)

        # Option 3: Désactiver mise en veille des cartes réseau (cochée par défaut)
        standard_vars['disable_network_sleep'] = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(col1,
                        text="✓ Désactiver veille cartes réseau",
                        variable=standard_vars['disable_network_sleep']).pack(anchor="w",
                                                                              padx=8,
                                                                              pady=1)

        # Option 3b: Mettre carte réseau en mode Privé (cochée par défaut)
        standard_vars['network_private'] = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(col1,
                        text="✓ Mettre carte réseau en mode Privé",
                        variable=standard_vars['network_private']).pack(anchor="w",
                                                                        padx=8,
                                                                        pady=1)

        # Option 4: Fuseau horaire + synchronisation (cochée par défaut)
        standard_vars['timezone_sync'] = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(col1,
                        text="✓ Fuseau horaire + sync",
                        variable=standard_vars['timezone_sync']).pack(anchor="w",
                                                                      padx=8,
                                                                      pady=1)

        # Option 5: Performances système (cochée par défaut)
        standard_vars['best_performance'] = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(col1,
                        text="✓ Meilleures performances",
                        variable=standard_vars['best_performance']).pack(anchor="w",
                                                                         padx=8,
                                                                         pady=1)

        # Option 6: Options d'alimentation (cochée par défaut)
        standard_vars['power_options'] = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(col1,
                        text="✓ Mode alimentation performance",
                        variable=standard_vars['power_options']).pack(anchor="w",
                                                                      padx=8,
                                                                      pady=1)

        # === OPTION 8: HEURES ACTIVES DU SYSTÈME ===
        standard_vars['active_hours'] = tk.BooleanVar(value=True)
        standard_vars['active_hours_start'] = tk.StringVar(value="8")
        standard_vars['active_hours_end'] = tk.StringVar(value="17")

        active_hours_frame = ctk.CTkFrame(col1, fg_color="transparent")
        active_hours_frame.pack(anchor="w", padx=8, pady=(6, 2))

        ctk.CTkCheckBox(active_hours_frame,
                        text="✓ Modifier heures actives",
                        variable=standard_vars['active_hours']).pack(anchor="w", pady=1)

        # Champ conditionnel pour les heures
        hours_input_frame = ctk.CTkFrame(active_hours_frame, fg_color="transparent")
        hours_input_frame.pack(anchor="w", padx=20, pady=(2, 0))

        ctk.CTkLabel(hours_input_frame, 
                     text="De :", 
                     font=ctk.CTkFont(size=10)).pack(side="left", padx=(0, 2))

        start_entry = ctk.CTkEntry(hours_input_frame,
                                   textvariable=standard_vars['active_hours_start'],
                                   width=40, height=22,
                                   font=ctk.CTkFont(size=10))
        start_entry.pack(side="left", padx=2)

        ctk.CTkLabel(hours_input_frame, 
                     text="h à :", 
                     font=ctk.CTkFont(size=10)).pack(side="left", padx=(4, 2))

        end_entry = ctk.CTkEntry(hours_input_frame,
                                 textvariable=standard_vars['active_hours_end'],
                                 width=40, height=22,
                                 font=ctk.CTkFont(size=10))
        end_entry.pack(side="left", padx=2)

        ctk.CTkLabel(hours_input_frame, 
                     text="h", 
                     font=ctk.CTkFont(size=10)).pack(side="left", padx=(0, 4))

        # Fonction pour activer/désactiver le champ conditionnel
        def toggle_hours_input():
            if standard_vars['active_hours'].get():
                start_entry.configure(state="normal")
                end_entry.configure(state="normal")
            else:
                start_entry.configure(state="disabled")
                end_entry.configure(state="disabled")

        # Activer par défaut si la checkbox est cochée
        if standard_vars['active_hours'].get():
            start_entry.configure(state="normal")
            end_entry.configure(state="normal")
        else:
            start_entry.configure(state="disabled")
            end_entry.configure(state="disabled")

        # Lier le changement de la checkbox
        standard_vars['active_hours'].trace_add('write', lambda *args: toggle_hours_input())

        # === OPTION 9: INSTALLATION NINITE (Notepad++, 7zip, Foxit, TightVNC) ===
        standard_vars['install_ninite'] = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(col1,
                        text="✓ Installer Ninite (Notepad++, 7zip, Foxit, TightVNC, TeamViewer)",
                        variable=standard_vars['install_ninite']).pack(anchor="w",
                                                                       padx=8,
                                                                       pady=(6, 1))

        # === OPTION 10: RÉTABLIR MENU CONTEXTUEL CLASSIQUE (Windows 11) ===
        standard_vars['restore_context_menu'] = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(col1,
                        text="✓ Rétablir menu contextuel classique (Win11)",
                        variable=standard_vars['restore_context_menu']).pack(anchor="w",
                                                                             padx=8,
                                                                             pady=(1, 4))

        # Statut partage protégé par mot de passe
        password_sharing_enabled = self._check_password_protected_sharing()

        status_pw_frame = ctk.CTkFrame(col1, fg_color="transparent")
        status_pw_frame.pack(anchor="w", padx=8, pady=(2, 1))

        ctk.CTkLabel(status_pw_frame,
                     text="🔒 Partage réseau :",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color="#fbbf24").pack(anchor="w")

        # --- Statut visuel ---
        if password_sharing_enabled:
            status_pw_text = "  🔒 Protégé par mot de passe"
            pw_color = "#f59e0b"
        else:
            status_pw_text = "  🔓 Ouvert (sans mot de passe)"
            pw_color = "#10b981"

        ctk.CTkLabel(status_pw_frame,
                     text=status_pw_text,
                     font=ctk.CTkFont(size=8),
                     text_color=pw_color).pack(anchor="w", padx=8, pady=(1, 1))

        # --- Choix d’action ---
        standard_vars['enable_password_sharing_config'] = tk.BooleanVar(value=True)
        standard_vars['password_sharing_action'] = tk.StringVar(value="Désactiver protection")


        ctk.CTkCheckBox(col1,
                        text="✓ Modifier protection partage",
                        variable=standard_vars['enable_password_sharing_config']).pack(anchor="w",
                                                                                       padx=8,
                                                                                       pady=(1, 1))

        pw_choice_frame = ctk.CTkFrame(col1, fg_color="transparent")
        pw_choice_frame.pack(anchor="w", padx=8, pady=(1, 4))

        ctk.CTkOptionMenu(
            pw_choice_frame,
            variable=standard_vars['password_sharing_action'],
            values=["Activer protection", "Désactiver protection"],
            width=180,
            height=22,
            font=ctk.CTkFont(size=10)).pack(anchor="w")


        # --- Clés de registre liées au partage réseau (repliables) ---
        reg_frame = ctk.CTkFrame(
            col1, fg_color="#1f2937")  # changer opt_frame → col1
        reg_frame.pack(fill="x", padx=6, pady=(4, 6))

        # Sous-frame pour les clés (masquée/affichée)
        reg_keys_frame = ctk.CTkFrame(reg_frame, fg_color="#1f2937")

        # État de visibilité
        reg_visible = tk.BooleanVar(value=False)

        def toggle_reg_keys():
            if reg_visible.get():
                # Masquer
                reg_keys_frame.pack_forget()
                arrow_label.configure(text="▸")  # flèche vers la droite
                reg_visible.set(False)
            else:
                # Afficher
                reg_keys_frame.pack(fill="x", padx=6, pady=(2, 4))
                arrow_label.configure(text="▾")  # flèche vers le bas
                reg_visible.set(True)

        # Ligne du titre avec flèche
        title_frame = ctk.CTkFrame(reg_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(4, 2))

        arrow_label = ctk.CTkLabel(title_frame,
                                   text="▸",
                                   text_color="#fbbf24",
                                   font=ctk.CTkFont(size=12, weight="bold"))
        arrow_label.pack(side="left", padx=(6, 2))

        title_label = ctk.CTkLabel(
            title_frame,
            text="🧩 Clés de registre modifié (partage réseau)",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#fbbf24")
        title_label.pack(side="left")

        # Permettre le clic sur la flèche et le texte
        arrow_label.bind("<Button-1>", lambda e: toggle_reg_keys())
        title_label.bind("<Button-1>", lambda e: toggle_reg_keys())

        # Liste des clés
        key_color = "#facc15"
        reg_keys = [
            "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Lsa\n → everyoneincludesanonymous",
            "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Lsa\n → ForceGuest",
            "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Lsa\n → restrictanonymous",
            "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\n → LocalAccountTokenFilterPolicy"
        ]

        for k in reg_keys:
            ctk.CTkLabel(reg_keys_frame,
                         text=k,
                         font=ctk.CTkFont(size=8),
                         text_color=key_color,
                         justify="left").pack(anchor="w", padx=10)

        # === COLONNE 2: SERVEUR + OPTIONS ===
        col2 = ctk.CTkFrame(content_frame, fg_color="transparent")
        col2.grid(row=0, column=1, sticky="nsew", padx=3)

        # Serveur
        serv_frame = ctk.CTkFrame(col2, fg_color="#2b2b2b")
        serv_frame.pack(fill="x", pady=(0, 3))

        ctk.CTkLabel(serv_frame,
                     text="🖥️ Poste Serveur",
                     font=ctk.CTkFont(size=12,
                                      weight="bold")).pack(pady=(6, 4))

        ctk.CTkCheckBox(serv_frame,
                        text="✓ Raccourcis Bureau VELBO/VELSRV",
                        variable=serveur_vars['shortcuts']).pack(anchor="w",
                                                                 padx=8,
                                                                 pady=1)

        # Option 2: Autoriser Veloce Backoffice dans pare-feu (PAS cochée par défaut)
        serveur_vars['allow_veloce_firewall'] = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(serv_frame,
                        text="✓ Veloce dans pare-feu",
                        variable=serveur_vars['allow_veloce_firewall']).pack(anchor="w",
                                                                             padx=8,
                                                                             pady=1)

        # Statut du dossier c:\veloce (affichage amélioré)
        veloce_exists, veloce_shared = self._check_veloce_share_status()

        status_frame = ctk.CTkFrame(serv_frame, fg_color="transparent")
        status_frame.pack(anchor="w", padx=8, pady=(6, 2))

        ctk.CTkLabel(status_frame,
                     text="📁 Dossier c:\\veloce:",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#fbbf24").pack(anchor="w")

        if veloce_exists:
            if veloce_shared:
                status_detail = "  ✅ Existe  |  ✅ Partagé"
                color = "#10b981"
            else:
                status_detail = "  ✅ Existe  |  ❌ Non partagé"
                color = "#f59e0b"
        else:
            status_detail = "  ❌ N'existe pas"
            color = "#ef4444"

        ctk.CTkLabel(status_frame,
                     text=status_detail,
                     font=ctk.CTkFont(size=9),
                     text_color=color).pack(anchor="w")

        ctk.CTkCheckBox(serv_frame,
                        text="✓ Partager c:\\veloce (Everyone - Contrôle total)",
                        variable=serveur_vars['share']).pack(anchor="w",
                                                             padx=8,
                                                             pady=(1, 6))

        # Options
        opt_frame = ctk.CTkFrame(col2, fg_color="#2b2b2b")
        opt_frame.pack(fill="x")

        ctk.CTkLabel(opt_frame,
                     text="⚙️ Options",
                     font=ctk.CTkFont(size=12,
                                      weight="bold")).pack(pady=(6, 4))

        #ctk.CTkLabel(opt_frame, 
        #             text=f"🖥️ Nom PC actuel : {current_pc_name}",
        #             font=ctk.CTkFont(size=10),
        #             text_color="#a5d6ff").pack(anchor="w", padx=8, pady=(2,4))

        ctk.CTkCheckBox(opt_frame, text="Renommer PC:",
                        variable=rename_var).pack(anchor="w", padx=8, pady=1)
        ctk.CTkEntry(opt_frame,
                     textvariable=pc_name_var,
                     placeholder_text="Nom",
                     width=140,
                     height=24).pack(anchor="w", padx=8, pady=1)

        ctk.CTkCheckBox(opt_frame,
                        text="Redémarrer auto",
                        variable=restart_var).pack(anchor="w",
                                                   padx=8,
                                                   pady=(2, 6))

        # === COLONNE 3: PROGRESSION / LOG ===
        col3 = ctk.CTkFrame(content_frame)
        col3.grid(row=0, column=2, sticky="nsew", padx=(3, 0))

        ctk.CTkLabel(col3,
                     text="📊 Progression",
                     font=ctk.CTkFont(size=11,
                                      weight="bold")).pack(pady=(6, 2))

        status_label_prog = ctk.CTkLabel(col3,
                                         text="Prêt...",
                                         font=ctk.CTkFont(size=10))
        status_label_prog.pack(pady=1)

        progress_bar = ctk.CTkProgressBar(col3, width=250)
        progress_bar.pack(pady=3)
        progress_bar.set(0)

        log_box = ctk.CTkTextbox(col3, width=250)
        log_box.pack(fill="both", expand=True, padx=6, pady=3)

        # Fonction pour exécuter
        def execute():

            def log_msg(msg):
                log_box.insert("end", msg + "\n")
                log_box.see("end")
                self.log(msg)

            def worker():
                try:
                    log_msg("===== AUTO SETUP: CONFIG PC =====")

                    # Collecter les étapes Standard
                    steps = []
                    if standard_vars['taskbar'].get():
                        steps.append(("Tweak barre des tâches",
                                      lambda: tweak_taskbar(self.log)))
                    if standard_vars['notifications'].get():
                        steps.append(
                            ("Désactivation notifications",
                             lambda: disable_windows_notifications(self.log)))
                    if standard_vars['user_admin'].get():
                        steps.append(
                            ("Création utilisateur 'admin'",
                             lambda: add_windows_user("admin", "veloce123",
                                                      True, True, self.log)))
                    if standard_vars['user_kpitech'].get():
                        steps.append(
                            ("Création utilisateur 'kpitech'",
                             lambda: add_windows_user("kpitech", "Log1tech",
                                                      True, True, self.log)))
                    if standard_vars['wallpaper'].get():
                        steps.append(
                            ("Application wallpaper KPI", lambda:
                             apply_wallpaper("wallpaper-kpi.jpg", self.log)))

                    # === NOUVELLES OPTIONS 1-8 ===

                    # Option 1: Désactiver UAC
                    if standard_vars['disable_uac'].get():
                        steps.append(
                            ("Désactivation UAC", lambda: self._disable_uac(log_msg)))


                    # Option 3: Désactiver veille cartes réseau
                    if standard_vars['disable_network_sleep'].get():
                        steps.append(
                            ("Désactivation veille réseau", lambda: self._disable_network_sleep(log_msg)))

                    # Option 3b: Mettre carte réseau en mode Privé
                    if standard_vars['network_private'].get():
                        steps.append(
                            ("Carte réseau en mode Privé", lambda: self._set_network_private(log_msg)))

                    # Option 4: Fuseau horaire + sync
                    if standard_vars['timezone_sync'].get():
                        steps.append(
                            ("Fuseau horaire + sync", lambda: self._set_timezone_and_sync(log_msg)))

                    # Option 5: Meilleures performances
                    if standard_vars['best_performance'].get():
                        steps.append(
                            ("Meilleures performances", lambda: self._set_best_performance(log_msg)))

                    # Option 6: Mode alimentation performance
                    if standard_vars['power_options'].get():
                        steps.append(
                            ("Mode alimentation performance", lambda: self._set_power_performance(log_msg)))

                    # Gestion partage protégé par mot de passe (Option 7)
                    # Vérifier si la checkbox est cochée
                    if standard_vars['enable_password_sharing_config'].get():
                        pw_action = standard_vars['password_sharing_action'].get()
                        if pw_action == "Activer protection":
                            steps.append(
                                ("Activation partage protégé", lambda: self.
                                 _enable_password_protected_sharing(log_msg)))
                        elif pw_action == "Désactiver protection":
                            steps.append(
                                ("Désactivation partage protégé", lambda: self.
                                 _disable_password_protected_sharing(log_msg)))

                    # Option 8: Heures actives
                    if standard_vars['active_hours'].get():
                        start_h = standard_vars['active_hours_start'].get()
                        end_h = standard_vars['active_hours_end'].get()
                        steps.append(
                            ("Configuration heures actives", 
                             lambda sh=start_h, eh=end_h: self._set_active_hours(log_msg, sh, eh)))

                    # Option 9: Installation Ninite
                    if standard_vars['install_ninite'].get():
                        steps.append(
                            ("Installation Ninite + config VNC", lambda: self._install_ninite(log_msg)))

                    # Option 10: Rétablir menu contextuel classique
                    if standard_vars['restore_context_menu'].get():
                        steps.append(
                            ("Rétablir menu contextuel classique", lambda: restore_context_menu(log_msg)))

                    # Collecter les étapes Serveur
                    if serveur_vars['shortcuts'].get():
                        steps.append(
                            ("Raccourcis VELBO/VELSRV",
                             lambda: self._create_serveur_shortcuts(log_msg)))
                    if serveur_vars['share'].get():
                        steps.append(
                            ("Partage c:\\veloce",
                             lambda: self._share_veloce_folder(log_msg)))

                    # Option 2: Pare-feu Veloce (dans serveur_vars)
                    if serveur_vars['allow_veloce_firewall'].get():
                        steps.append(
                            ("Configuration pare-feu Veloce", lambda: self._allow_veloce_firewall(log_msg)))

                    if not steps:
                        log_msg("⚠️ Aucune étape sélectionnée")
                        status_label_prog.configure(
                            text="⚠️ Aucune étape sélectionnée")
                        return

                    total = len(steps)

                    # Exécuter
                    for i, (name, action) in enumerate(steps, 1):
                        status_label_prog.configure(
                            text=f"▶ Étape {i}/{total}: {name}...")
                        log_msg(f"▶ Étape {i}/{total}: {name}...")
                        try:
                            action()
                            log_msg("✅ Terminé")
                        except Exception as e:
                            log_msg(f"❌ Erreur: {e}")
                        progress_bar.set(i / total)
                        time.sleep(0.5)

                    # Renommer PC
                    if rename_var.get():
                        new_name = pc_name_var.get().strip()
                        if new_name:
                            status_label_prog.configure(
                                text="▶ Renommage du PC...")
                            log_msg(f"▶ Renommage du PC en '{new_name}'...")
                            try:
                                rename_computer(new_name, self.log)
                                log_msg("✅ PC renommé")
                            except Exception as e:
                                log_msg(f"❌ Erreur renommage: {e}")

                    status_label_prog.configure(
                        text="✅ Configuration terminée!")
                    log_msg("=" * 50)
                    log_msg("✅ AUTO SETUP CONFIG PC TERMINÉ!")

                    # Redémarrage
                    if restart_var.get() and rename_var.get(
                    ) and pc_name_var.get().strip():
                        log_msg("🔄 Redémarrage dans 10 secondes...")
                        subprocess.run("shutdown /r /t 10", shell=True)

                except Exception as e:
                    log_msg(f"❌ Erreur fatale: {e}")
                    status_label_prog.configure(text="❌ Erreur")

            log_box.delete("1.0", "end")
            progress_bar.set(0)
            threading.Thread(target=worker, daemon=True).start()

        # Bouton démarrer
        ctk.CTkButton(main_frame,
                      text="🚀 Démarrer la configuration",
                      width=350,
                      height=40,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color="#16a34a",
                      hover_color="#15803d",
                      command=execute).pack(pady=10)

    def _create_serveur_shortcuts(self, log_fn):
        """Crée les raccourcis VELBO/VELSRV et copie VELSRV au démarrage"""
        veloce_path = r"c:\veloce"

        if not os.path.exists(veloce_path):
            log_fn(f"❌ Le dossier {veloce_path} n'existe pas")
            return

        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            startup = os.path.join(os.path.expanduser("~"), "AppData",
                                   "Roaming", "Microsoft", "Windows",
                                   "Start Menu", "Programs", "Startup")

            ps_script = f'''
[System.Threading.Thread]::CurrentThread.ApartmentState = [System.Threading.ApartmentState]::STA
$WshShell = New-Object -comObject WScript.Shell

# VELBO sur le bureau
$Shortcut1 = $WshShell.CreateShortcut("{os.path.join(desktop, 'VELBO.lnk')}")
$Shortcut1.TargetPath = "{os.path.join(veloce_path, 'velbo.exe')}"
$Shortcut1.WorkingDirectory = "{veloce_path}"
$Shortcut1.Save()

# VELSRV sur le bureau (avec 2e icône)
$Shortcut2 = $WshShell.CreateShortcut("{os.path.join(desktop, 'VELSRV.lnk')}")
$Shortcut2.TargetPath = "{os.path.join(veloce_path, 'velsrv.exe')}"
$Shortcut2.WorkingDirectory = "{veloce_path}"
$Shortcut2.IconLocation = "{os.path.join(veloce_path, 'velsrv.exe')},1"
$Shortcut2.Save()

# VELSRV au démarrage
$Shortcut3 = $WshShell.CreateShortcut("{os.path.join(startup, 'VELSRV.lnk')}")
$Shortcut3.TargetPath = "{os.path.join(veloce_path, 'velsrv.exe')}"
$Shortcut3.WorkingDirectory = "{veloce_path}"
$Shortcut3.IconLocation = "{os.path.join(veloce_path, 'velsrv.exe')},1"
$Shortcut3.Save()
'''

            subprocess.run(["powershell", "-Command", ps_script],
                           capture_output=True,
                           text=True,
                           check=True)

            log_fn("✅ VELBO.lnk créé sur le Bureau")
            log_fn("✅ VELSRV.lnk créé sur le Bureau")
            log_fn("✅ VELSRV.lnk copié au Démarrage")

        except Exception as e:
            log_fn(f"❌ Erreur création raccourcis: {e}")

    def _share_veloce_folder(self, log_fn):
        """Partage le dossier c:\\veloce avec Everyone (accès intégral)"""
        veloce_path = r"c:\veloce"

        # Créer le dossier s'il n'existe pas
        if not os.path.exists(veloce_path):
            log_fn(f"▶ Création du dossier {veloce_path}...")
            try:
                os.makedirs(veloce_path, exist_ok=True)
                log_fn(f"✅ Dossier créé: {veloce_path}")
            except Exception as e:
                log_fn(f"❌ Impossible de créer le dossier: {e}")
                return

        try:
            # ÉTAPE 1: Définir les permissions NTFS pour Everyone (Contrôle total)
            log_fn("▶ Configuration des permissions NTFS pour Everyone...")
            ntfs_cmd = f'icacls "{veloce_path}" /grant Everyone:(OI)(CI)F /T /C /Q'

            result_ntfs = subprocess.run(ntfs_cmd,
                                         shell=True,
                                         capture_output=True,
                                         text=True)
            if result_ntfs.returncode == 0:
                log_fn("✅ Permissions NTFS: Everyone = Contrôle total")
            else:
                log_fn(f"⚠️ Avertissement NTFS: {result_ntfs.stderr}")

            # ÉTAPE 2: Supprimer le partage réseau existant si présent
            subprocess.run('net share veloce /delete',
                           shell=True,
                           capture_output=True)

            # ÉTAPE 3: Créer le nouveau partage réseau avec Everyone Full
            log_fn("▶ Création du partage réseau...")
            share_cmd = f'net share veloce={veloce_path} /grant:everyone,full'

            result_share = subprocess.run(share_cmd,
                                          shell=True,
                                          capture_output=True,
                                          text=True,
                                          check=True)

            log_fn("✅ Partage réseau créé: \\\\<PC>\\veloce")
            log_fn("✅ Permissions partage: Everyone = Contrôle total")
            log_fn("✅ Dossier c:\\veloce partagé avec succès")

        except subprocess.CalledProcessError as e:
            log_fn(f"❌ Erreur lors du partage réseau: {e.stderr}")
        except Exception as e:
            log_fn(f"❌ Erreur partage dossier: {e}")

    def _open_veloce_window(self):
        """Ouvre la fenêtre Station Veloce avec les 2 champs visibles"""
        from tkinter import Toplevel

        window = Toplevel(self)
        window.title("Auto Setup - Station Veloce")
        window.geometry("900x650")
        window.resizable(True, True)
        window.transient(self)
        window.grab_set()

        # Frame principal
        main_frame = ctk.CTkFrame(window)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Titre
        ctk.CTkLabel(main_frame,
                     text="💳 Configuration Station Veloce",
                     font=ctk.CTkFont(size=16,
                                      weight="bold")).pack(pady=(0, 10))

        server_var = tk.StringVar(value="SV")
        station_var = tk.StringVar(value="")

        # Container horizontal: Paramètres GAUCHE | Log DROITE
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=(0, 8))

        # === GAUCHE: Paramètres ===
        left_frame = ctk.CTkFrame(content_frame, fg_color="#2b2b2b")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))

        ctk.CTkLabel(left_frame,
                     text="💳 Étapes de configuration :",
                     font=ctk.CTkFont(size=14,
                                      weight="bold")).pack(anchor="w",
                                                           padx=10,
                                                           pady=(8, 4))

        desc_text = """✓ Vérification accès réseau
✓ Installation install (WSXX).exe
✓ Raccourci bureau
✓ Clé registre + Démarrage"""
        ctk.CTkLabel(left_frame,
                     text=desc_text,
                     justify="left",
                     font=ctk.CTkFont(size=12)).pack(anchor="w",
                                                     padx=12,
                                                     pady=(0, 8))

        ctk.CTkLabel(left_frame,
                     text="⚙️ Paramètres :",
                     font=ctk.CTkFont(size=14,
                                      weight="bold")).pack(anchor="w",
                                                           padx=10,
                                                           pady=(4, 4))

        # Serveur
        ctk.CTkLabel(left_frame,
                     text="Nom du serveur:",
                     font=ctk.CTkFont(size=12)).pack(anchor="w",
                                                     padx=12,
                                                     pady=(4, 2))
        ctk.CTkEntry(left_frame,
                     textvariable=server_var,
                     width=220,
                     height=26,
                     placeholder_text="Ex: SV",
                     font=ctk.CTkFont(size=12)).pack(anchor="w",
                                                     padx=12,
                                                     pady=2)

        # Station
        ctk.CTkLabel(left_frame,
                     text="Numéro de station:",
                     font=ctk.CTkFont(size=12)).pack(anchor="w",
                                                     padx=12,
                                                     pady=(6, 2))
        ctk.CTkEntry(left_frame,
                     textvariable=station_var,
                     width=220,
                     height=26,
                     placeholder_text="Ex: 1, 2, 15...",
                     font=ctk.CTkFont(size=12)).pack(anchor="w",
                                                     padx=12,
                                                     pady=2)

        # Info chemin
        ctk.CTkLabel(left_frame,
                     text="ℹ️ \\\\[SERVEUR]\\veloce\\stat[XX]\\install\\",
                     font=ctk.CTkFont(size=12),
                     text_color="#a5d6ff").pack(anchor="w",
                                                padx=12,
                                                pady=(8, 8))

        # === DROITE: Progression ===
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(right_frame,
                     text="📊 Progression",
                     font=ctk.CTkFont(size=14,
                                      weight="bold")).pack(pady=(8, 4))

        status_label = ctk.CTkLabel(right_frame,
                                    text="Prêt à démarrer...",
                                    font=ctk.CTkFont(size=12))
        status_label.pack(pady=2)

        progress_bar = ctk.CTkProgressBar(right_frame, width=280)
        progress_bar.pack(pady=3)
        progress_bar.set(0)

        log_box = ctk.CTkTextbox(right_frame, width=300)
        log_box.pack(fill="both", expand=True, padx=6, pady=6)

        # Fonction exécution
        def execute():
            server = server_var.get().strip()
            station = station_var.get().strip()

            if not server:
                messagebox.showerror("Erreur",
                                     "Veuillez entrer le nom du serveur",
                                     parent=window)
                return

            if not station or not station.isdigit():
                messagebox.showerror(
                    "Erreur",
                    "Veuillez entrer un numéro de station valide (1-99)",
                    parent=window)
                return

            station_num = int(station)
            if station_num < 1 or station_num > 99:
                messagebox.showerror(
                    "Erreur",
                    "Le numéro de station doit être entre 1 et 99",
                    parent=window)
                return

            # Lancer la configuration
            log_box.delete("1.0", "end")
            progress_bar.set(0)
            self._run_auto_setup_veloce_inline(window, server, station_num,
                                               status_label, progress_bar,
                                               log_box)

        # Bouton démarrer
        ctk.CTkButton(main_frame,
                      text="🚀 Démarrer l'installation",
                      width=350,
                      height=42,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color="#2563eb",
                      hover_color="#1d4ed8",
                      command=execute).pack(pady=6)

    def _run_auto_setup_veloce_inline(self, window, server, station_num,
                                      status_label, progress_bar, log_box):
        """Exécute Station Veloce dans la fenêtre (pas de popup)"""

        def log_msg(msg):
            log_box.insert("end", msg + "\n")
            log_box.see("end")
            self.log(msg)

        def worker():
            try:
                log_msg(f"===== AUTO SETUP: STATION VELOCE =====")

                # Format station
                station_formatted = f"{station_num:02d}"
                station_no_zero = str(station_num)

                log_msg(f"Serveur: {server}")
                log_msg(
                    f"Numéro de station: {station_num} (formaté: {station_formatted})"
                )
                progress_bar.set(0.1)

                # Chemins
                veloce_base = f"\\\\{server}\\veloce"
                station_folder = f"stat{station_formatted}"
                station_path = os.path.join(veloce_base, station_folder,
                                            "install")
                install_exe = os.path.join(
                    station_path, f"install (WS{station_formatted}).exe")
                ws_starter = os.path.join(station_path,
                                          f"WS Starter{station_no_zero}.exe")
                desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                appdata = os.getenv("APPDATA") or os.path.expanduser("~")
                startup_folder = os.path.join(appdata, "Microsoft", "Windows",
                                              "Start Menu", "Programs",
                                              "Startup")

                # Étape 1: Ping serveur
                status_label.configure(text="Vérification accès réseau...")
                log_msg(f"▶ Vérification accès à {veloce_base}...")

                ping_result = subprocess.run(f"ping -n 1 -w 1000 {server}",
                                             shell=True,
                                             capture_output=True,
                                             timeout=2)

                if ping_result.returncode != 0:
                    log_msg(f"❌ Serveur {server} non joignable")
                    status_label.configure(text="❌ Serveur non joignable")
                    progress_bar.set(1.0)
                    return

                log_msg(f"✓ Serveur {server} joignable")

                if not os.path.exists(station_path):
                    log_msg(f"❌ Dossier {station_folder} introuvable")
                    log_msg(f"Chemin: {station_path}")
                    status_label.configure(
                        text="❌ Dossier station introuvable")
                    progress_bar.set(1.0)
                    return

                log_msg(f"✓ Dossier station accessible: {station_path}")
                progress_bar.set(0.2)

                # Étape 2: Installer
                status_label.configure(text="Installation de l'application...")
                log_msg(
                    f"▶ Lancement de install (WS{station_formatted}).exe en mode admin..."
                )

                if not os.path.exists(install_exe):
                    log_msg(f"❌ Fichier introuvable: {install_exe}")
                    status_label.configure(
                        text="❌ Fichier install introuvable")
                    progress_bar.set(1.0)
                    return

                import ctypes
                ret = ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", install_exe, None, station_path, 1)

                if ret > 32:
                    log_msg(
                        f"✓ install (WS{station_formatted}).exe lancé avec succès"
                    )
                else:
                    log_msg(f"❌ Échec du lancement (code: {ret})")
                    status_label.configure(text="❌ Erreur installation")
                    progress_bar.set(1.0)
                    return

                progress_bar.set(0.4)
                time.sleep(1)

                # Étape 3: Raccourci bureau
                status_label.configure(text="Création du raccourci bureau...")
                log_msg(
                    f"▶ Création du raccourci 'station {station_no_zero}' sur le bureau..."
                )

                if not os.path.exists(ws_starter):
                    log_msg(f"❌ Fichier source introuvable: {ws_starter}")
                    status_label.configure(text="❌ WS Starter introuvable")
                    progress_bar.set(1.0)
                    return

                shortcut_path = os.path.join(desktop,
                                             f"station {station_no_zero}.lnk")
                ps_script = f'''
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{ws_starter}"
$Shortcut.WorkingDirectory = "{station_path}"
$Shortcut.Save()
'''
                ps_cmd = [
                    'powershell', '-ExecutionPolicy', 'Bypass', '-Command',
                    ps_script
                ]
                result = subprocess.run(ps_cmd, capture_output=True, text=True)

                if result.returncode == 0 and os.path.exists(shortcut_path):
                    log_msg(f"✓ Raccourci créé: {shortcut_path}")
                else:
                    log_msg(f"❌ Erreur création raccourci: {result.stderr}")
                    log_msg("⚠️ Continuez manuellement...")

                progress_bar.set(0.6)

                # Étape 4: Copier raccourci au démarrage (supprimer l'existant d'abord)
                status_label.configure(text="Copie raccourci au démarrage...")
                log_msg(f"▶ Copie du raccourci dans le dossier Démarrage...")

                startup_shortcut = os.path.join(
                    startup_folder, f"station {station_no_zero}.lnk")

                # Supprimer l'ancien raccourci s'il existe
                if os.path.exists(startup_shortcut):
                    try:
                        os.remove(startup_shortcut)
                        log_msg(f"✓ Ancien raccourci supprimé du démarrage")
                    except Exception as e:
                        log_msg(
                            f"⚠️ Impossible de supprimer l'ancien raccourci: {e}"
                        )

                # Créer le nouveau raccourci dans le démarrage
                ps_script_startup = f'''
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut("{startup_shortcut}")
$Shortcut.TargetPath = "{ws_starter}"
$Shortcut.WorkingDirectory = "{station_path}"
$Shortcut.Save()
'''
                result_startup = subprocess.run([
                    'powershell', '-ExecutionPolicy', 'Bypass', '-Command',
                    ps_script_startup
                ],
                                                capture_output=True,
                                                text=True)

                if result_startup.returncode == 0 and os.path.exists(
                        startup_shortcut):
                    log_msg(
                        f"✓ Raccourci copié au démarrage: {startup_shortcut}")
                else:
                    log_msg(
                        f"❌ Erreur copie démarrage: {result_startup.stderr}")

                # Supprimer l'ancien "Veloce WS Starter" du démarrage (.lnk ET .exe)
                log_msg(f"▶ Nettoyage ancien raccourci 'Veloce WS Starter'...")

                deleted_count = 0
                # Chercher variante .lnk
                old_lnk = os.path.join(startup_folder, "Veloce WS Starter.lnk")
                if os.path.exists(old_lnk):
                    try:
                        os.remove(old_lnk)
                        log_msg(f"✓ 'Veloce WS Starter.lnk' supprimé")
                        deleted_count += 1
                    except Exception as e:
                        log_msg(f"⚠️ Erreur suppression .lnk: {e}")

                # Chercher variante .exe
                old_exe = os.path.join(startup_folder, "Veloce WS Starter.exe")
                if os.path.exists(old_exe):
                    try:
                        os.remove(old_exe)
                        log_msg(f"✓ 'Veloce WS Starter.exe' supprimé")
                        deleted_count += 1
                    except Exception as e:
                        log_msg(f"⚠️ Erreur suppression .exe: {e}")

                if deleted_count == 0:
                    log_msg(f"✓ Pas d'ancien 'Veloce WS Starter' à supprimer")

                progress_bar.set(0.8)

                # Étape 5: Clé de registre DirectoryCacheLifetime
                status_label.configure(text="Application clé registre...")
                log_msg(
                    f"▶ Application de la clé registre DirectoryCacheLifetime..."
                )

                try:
                    import winreg
                    key_path = r"SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters"
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path,
                                         0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, "DirectoryCacheLifetime", 0,
                                      winreg.REG_DWORD, 0)
                    winreg.CloseKey(key)
                    log_msg(
                        f"✓ Clé registre DirectoryCacheLifetime définie à 0")
                except Exception as e:
                    log_msg(f"❌ Erreur clé registre: {e}")
                    log_msg("⚠️ Nécessite droits administrateur")

                progress_bar.set(0.9)

                # Terminé
                status_label.configure(text="✅ Configuration terminée!")
                log_msg("=" * 50)
                log_msg("✅ AUTO SETUP STATION VELOCE TERMINÉ!")
                log_msg(f"✓ Raccourci bureau: 'station {station_no_zero}'")
                log_msg(f"✓ Raccourci démarrage Windows")
                log_msg(f"✓ Clé registre DirectoryCacheLifetime = 0")
                progress_bar.set(1.0)

            except Exception as e:
                log_msg(f"❌ Erreur fatale: {e}")
                status_label.configure(text="❌ Erreur")

        threading.Thread(target=worker, daemon=True).start()

    def _build_standard_ui(self):
        """Construit l'UI pour Poste Standard"""
        frame = self._auto_config_frame

        # Description
        desc_frame = ctk.CTkFrame(frame, fg_color="#2b2b2b")
        desc_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(desc_frame,
                     text="📋 Sélectionnez les étapes à exécuter :",
                     font=ctk.CTkFont(size=13,
                                      weight="bold")).pack(anchor="w",
                                                           padx=20,
                                                           pady=(15, 10))

        # Checkboxes pour les étapes
        if not hasattr(self, '_standard_steps_vars'):
            self._standard_steps_vars = {
                'taskbar': tk.BooleanVar(value=True),
                'notifications': tk.BooleanVar(value=True),
                'user_admin': tk.BooleanVar(value=True),
                'user_kpitech': tk.BooleanVar(value=True),
                'wallpaper': tk.BooleanVar(value=True),
            }
            self._standard_rename_var = tk.BooleanVar(value=False)
            # Utiliser la MÊME variable que la page "Renommer PC" (ligne 82-83)
            # Pas besoin de créer _standard_pc_name_var, on utilise self.pc_name_var
            self._standard_restart_var = tk.BooleanVar(value=False)

        checks_frame = ctk.CTkFrame(desc_frame, fg_color="transparent")
        checks_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkCheckBox(checks_frame,
                        text="✓ Tweak barre des tâches",
                        variable=self._standard_steps_vars['taskbar']).pack(
                            anchor="w", pady=3)
        ctk.CTkCheckBox(
            checks_frame,
            text="✓ Désactiver notifications Windows",
            variable=self._standard_steps_vars['notifications']).pack(
                anchor="w", pady=3)
        ctk.CTkCheckBox(checks_frame,
                        text="✓ Créer utilisateur 'admin' (veloce123)",
                        variable=self._standard_steps_vars['user_admin']).pack(
                            anchor="w", pady=3)
        ctk.CTkCheckBox(
            checks_frame,
            text="✓ Créer utilisateur 'kpitech' (Log1tech)",
            variable=self._standard_steps_vars['user_kpitech']).pack(
                anchor="w", pady=3)
        ctk.CTkCheckBox(checks_frame,
                        text="✓ Appliquer wallpaper KPI",
                        variable=self._standard_steps_vars['wallpaper']).pack(
                            anchor="w", pady=3)

        # Options supplémentaires
        options_frame = ctk.CTkFrame(frame)
        options_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(options_frame,
                     text="⚙️ Options supplémentaires :",
                     font=ctk.CTkFont(size=13,
                                      weight="bold")).pack(anchor="w",
                                                           padx=20,
                                                           pady=(15, 10))

        # Renommer PC
        rename_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        rename_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkCheckBox(rename_frame,
                        text="Renommer le PC :",
                        variable=self._standard_rename_var).pack(side="left")

        # FORCER le nom actuel du PC dans le champ immédiatement
        current_pc_name = os.environ.get("COMPUTERNAME", "")
        if not self.pc_name_var.get() or self.pc_name_var.get() != current_pc_name:
            self.pc_name_var.set(current_pc_name)

        pc_entry = ctk.CTkEntry(rename_frame, width=250)
        pc_entry.insert(0, current_pc_name)  # Forcer l'affichage direct
        pc_entry.pack(side="left", padx=10)

        # Synchroniser avec self.pc_name_var pour la suite
        def sync_pc_name(*args):
            self.pc_name_var.set(pc_entry.get())
        pc_entry.bind('<KeyRelease>', sync_pc_name)

        # Label avec le nom actuel
       # ctk.CTkLabel(rename_frame, 
       #              text=f"(Actuel: {current_pc_name})",
       #              text_color="#9ca3af",
       #              font=ctk.CTkFont(size=11)).pack(side="left", padx=5)

        # Redémarrage
        ctk.CTkCheckBox(options_frame,
                        text="Redémarrer automatiquement après configuration",
                        variable=self._standard_restart_var).pack(anchor="w",
                                                                  padx=20,
                                                                  pady=(10,
                                                                        15))

        # Zone de progression
        self._standard_progress_frame = ctk.CTkFrame(frame)
        self._standard_progress_frame.pack(fill="both",
                                           expand=True,
                                           padx=15,
                                           pady=10)

        self._standard_status_label = ctk.CTkLabel(
            self._standard_progress_frame,
            text="Prêt à démarrer...",
            font=ctk.CTkFont(size=12))
        self._standard_status_label.pack(pady=10)

        self._standard_progress_bar = ctk.CTkProgressBar(
            self._standard_progress_frame, width=400)
        self._standard_progress_bar.pack(pady=10)
        self._standard_progress_bar.set(0)

        self._standard_log_box = ctk.CTkTextbox(self._standard_progress_frame,
                                                height=150)
        self._standard_log_box.pack(fill="both", expand=True, padx=10, pady=10)

        # Bouton démarrer
        ctk.CTkButton(frame,
                      text="🚀 Démarrer la configuration",
                      width=300,
                      height=45,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      fg_color="#16a34a",
                      hover_color="#15803d",
                      command=self._start_standard_setup).pack(pady=20)

    def _start_standard_setup(self):
        """Démarre la configuration Standard (inline, sans popup)"""

        def log_inline(msg):
            """Ajoute un message au log inline"""
            self._standard_log_box.insert("end", msg + "\n")
            self._standard_log_box.see("end")
            self.log(msg)

        def worker():
            try:
                log_inline("===== AUTO SETUP: POSTE STANDARD =====")

                # Collecter les étapes à exécuter
                steps = []
                if self._standard_steps_vars['taskbar'].get():
                    steps.append(("Tweak barre des tâches",
                                  lambda: tweak_taskbar(self.log)))
                if self._standard_steps_vars['notifications'].get():
                    steps.append(
                        ("Désactivation notifications",
                         lambda: disable_windows_notifications(self.log)))
                if self._standard_steps_vars['user_admin'].get():
                    steps.append(
                        ("Création utilisateur 'admin'",
                         lambda: add_windows_user("admin", "veloce123", True,
                                                  True, self.log)))
                if self._standard_steps_vars['user_kpitech'].get():
                    steps.append(
                        ("Création utilisateur 'kpitech'",
                         lambda: add_windows_user("kpitech", "Log1tech", True,
                                                  True, self.log)))
                if self._standard_steps_vars['wallpaper'].get():
                    steps.append(
                        ("Application wallpaper KPI",
                         lambda: apply_wallpaper("wallpaper-kpi.jpg", self.log)
                         ))

                if not steps:
                    log_inline("⚠️ Aucune étape sélectionnée")
                    self._standard_status_label.configure(
                        text="⚠️ Aucune étape sélectionnée")
                    return

                total = len(steps)

                # Exécuter les étapes
                for i, (name, action) in enumerate(steps, 1):
                    self._standard_status_label.configure(
                        text=f"▶ Étape {i}/{total}: {name}...")
                    log_inline(f"▶ Étape {i}/{total}: {name}...")

                    try:
                        action()
                        log_inline("✅ Terminé")
                    except Exception as e:
                        log_inline(f"❌ Erreur: {e}")

                    self._standard_progress_bar.set(i / total)
                    time.sleep(0.5)

                # Renommer le PC si demandé
                if self._standard_rename_var.get():
                    new_name = self.pc_name_var.get().strip()
                    if new_name:
                        self._standard_status_label.configure(
                            text="▶ Renommage du PC...")
                        log_inline(f"▶ Renommage du PC en '{new_name}'...")
                        try:
                            rename_computer(new_name, self.log)
                            log_inline("✅ PC renommé avec succès")
                        except Exception as e:
                            log_inline(f"❌ Erreur renommage: {e}")
                    else:
                        log_inline(
                            "⚠️ Renommage demandé mais aucun nom fourni")

                self._standard_status_label.configure(
                    text="✅ Configuration terminée!")
                log_inline("=" * 50)
                log_inline("✅ AUTO SETUP POSTE STANDARD TERMINÉ!")

                # Redémarrage si demandé
                if self._standard_restart_var.get():
                    if self._standard_rename_var.get(
                    ) and self.pc_name_var.get().strip():
                        log_inline(
                            "🔄 Redémarrage du système dans 10 secondes...")
                        subprocess.run("shutdown /r /t 10", shell=True)
                        log_inline("✅ Redémarrage planifié")

            except Exception as e:
                log_inline(f"❌ Erreur fatale: {e}")
                self._standard_status_label.configure(text="❌ Erreur")

        # Réinitialiser l'UI
        self._standard_log_box.delete("1.0", "end")
        self._standard_progress_bar.set(0)

        # Lancer en thread
        threading.Thread(target=worker, daemon=True).start()

    def _build_serveur_ui(self):
        """Construit l'UI pour Poste Serveur"""
        frame = self._auto_config_frame

        info_frame = ctk.CTkFrame(frame, fg_color="#3a3a3a")
        info_frame.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(info_frame,
                     text="⚠️ Configuration en attente",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#fbbf24").pack(pady=(30, 10))

        ctk.CTkLabel(
            info_frame,
            text=
            "La configuration automatique pour Poste Serveur\nest en cours de définition.",
            font=ctk.CTkFont(size=12),
            justify="center").pack(pady=(0, 30))

    def _build_veloce_ui(self):
        """Construit l'UI pour Station Veloce"""
        frame = self._auto_config_frame

        # Description
        desc_frame = ctk.CTkFrame(frame, fg_color="#2b2b2b")
        desc_frame.pack(fill="x", padx=15, pady=10)

        desc_text = """💳 Configuration Station Veloce :

✓ Vérification accès réseau au serveur
✓ Installation de install (WSXX).exe en mode admin
✓ Création raccourci bureau "station X"
✓ Application clé registre DirectoryCacheLifetime
✓ Copie dans Démarrage Windows
✓ Suppression ancien raccourci Veloce"""

        ctk.CTkLabel(desc_frame,
                     text=desc_text,
                     justify="left",
                     font=ctk.CTkFont(size=11)).pack(padx=20, pady=15)

        # Champs de saisie
        if not hasattr(self, '_veloce_server_var'):
            self._veloce_server_var = tk.StringVar(value="")
            self._veloce_station_var = tk.StringVar(value="")

        fields_frame = ctk.CTkFrame(frame)
        fields_frame.pack(fill="x", padx=15, pady=10)

        # Nom du serveur
        row1 = ctk.CTkFrame(fields_frame, fg_color="transparent")
        row1.pack(fill="x", pady=8)
        ctk.CTkLabel(row1,
                     text="Nom du serveur:",
                     width=150,
                     anchor="w",
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
        ctk.CTkEntry(row1,
                     textvariable=self._veloce_server_var,
                     width=300,
                     placeholder_text="Ex: SV",
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=10)

        # Numéro de station
        row2 = ctk.CTkFrame(fields_frame, fg_color="transparent")
        row2.pack(fill="x", pady=8)
        ctk.CTkLabel(row2,
                     text="Numéro de station:",
                     width=150,
                     anchor="w",
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=10)
        ctk.CTkEntry(row2,
                     textvariable=self._veloce_station_var,
                     width=300,
                     placeholder_text="Ex: 1, 2, 15...",
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=10)

        # Info chemin
        info_frame = ctk.CTkFrame(frame, fg_color="#3a3a3a")
        info_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            info_frame,
            text=
            "ℹ️ Le chemin utilisé sera: \\\\[SERVEUR]\\veloce\\stat[XX]\\install\\",
            font=ctk.CTkFont(size=10),
            text_color="#a5d6ff").pack(padx=15, pady=10)

        # Bouton démarrer
        ctk.CTkButton(frame,
                      text="🚀 Démarrer l'installation",
                      width=300,
                      height=45,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      fg_color="#2563eb",
                      hover_color="#1d4ed8",
                      command=self._start_veloce_setup).pack(pady=20)

    def _start_veloce_setup(self):
        """Démarre la configuration Station Veloce"""
        server = self._veloce_server_var.get().strip()
        station = self._veloce_station_var.get().strip()

        if not server:
            messagebox.showerror("Erreur", "Veuillez entrer le nom du serveur")
            return

        if not station or not station.isdigit():
            messagebox.showerror(
                "Erreur", "Veuillez entrer un numéro de station valide (1-99)")
            return

        station_num = int(station)
        if station_num < 1 or station_num > 99:
            messagebox.showerror(
                "Erreur", "Le numéro de station doit être entre 1 et 99")
            return

        # Lancer la configuration avec les paramètres
        self._run_auto_setup("veloce",
                             server_name=server,
                             station_number=station_num)

    def _run_auto_setup(self,
                        setup_type,
                        server_name=None,
                        station_number=None):
        """Exécute la configuration automatique selon le type avec dialogue step-by-step"""
        from tkinter import Toplevel, messagebox

        # Fenêtre de dialogue
        dialog = Toplevel(self)
        dialog.title(f"Auto Setup - {setup_type.upper()}")
        dialog.geometry("750x650")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Frame principal
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Titre
        ctk.CTkLabel(main_frame,
                     text=f"Configuration {setup_type.upper()}",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        # Label pour l'étape courante
        step_label = ctk.CTkLabel(main_frame,
                                  text="Prêt à démarrer...",
                                  font=ctk.CTkFont(size=13))
        step_label.pack(pady=10)

        # Barre de progression
        progress_bar = ctk.CTkProgressBar(main_frame, width=400)
        progress_bar.pack(pady=10)
        progress_bar.set(0)

        # Log frame
        log_frame = ctk.CTkTextbox(main_frame, width=550, height=200)
        log_frame.pack(pady=10, fill="both", expand=True)

        def log_to_dialog(msg):
            """Ajoute un message au log de la fenêtre"""
            log_frame.insert("end", msg + "\n")
            log_frame.see("end")
            self.log(msg)

        def run_worker(server_name=None, station_number=None):
            """Exécute les étapes de configuration"""
            log_to_dialog(f"===== AUTO SETUP: {setup_type.upper()} =====")

            if setup_type == "standard":
                steps = [
                    ("Tweak barre des tâches",
                     lambda: tweak_taskbar(self.log)),
                    ("Désactivation notifications",
                     lambda: disable_windows_notifications(self.log)),
                    ("Création utilisateur 'admin'", lambda: add_windows_user(
                        "admin", "veloce123", True, True, self.log)),
                    ("Création utilisateur 'kpitech'",
                     lambda: add_windows_user("kpitech", "Log1tech", True,
                                              True, self.log)),
                    ("Application wallpaper KPI",
                     lambda: apply_wallpaper("wallpaper-kpi.jpg", self.log))
                ]

                pc_renamed = False
                total = len(steps)
                for i, (name, action) in enumerate(steps, 1):
                    # Demander confirmation
                    dialog.update()
                    result = messagebox.askyesno(
                        "Confirmation",
                        f"Étape {i}/{total}: {name}\n\nExécuter cette étape ?",
                        parent=dialog)

                    if result:
                        step_label.configure(
                            text=f"▶ Étape {i}/{total}: {name}...")
                        log_to_dialog(f"▶ Étape {i}/{total}: {name}...")
                        try:
                            action()
                            log_to_dialog("✅ Terminé")
                        except Exception as e:
                            log_to_dialog(f"❌ Erreur: {e}")
                    else:
                        log_to_dialog(f"⏭️ Étape {i}/{total} ignorée: {name}")

                    progress_bar.set(i / total)
                    time.sleep(0.5)

                # Étape supplémentaire : Renommer le PC ?
                dialog.update()
                if messagebox.askyesno(
                        "Renommer le PC ?",
                        "Voulez-vous renommer ce PC ?\n\n(Un redémarrage sera nécessaire)",
                        parent=dialog):
                    from tkinter import simpledialog
                    new_name = simpledialog.askstring(
                        "Nouveau nom du PC",
                        "Entrez le nouveau nom du PC:",
                        parent=dialog)
                    if new_name and new_name.strip():
                        step_label.configure(text="▶ Renommage du PC...")
                        log_to_dialog(
                            f"▶ Renommage du PC en '{new_name.strip()}'...")
                        try:
                            rename_computer(new_name.strip(), self.log)
                            log_to_dialog("✅ PC renommé avec succès")
                            pc_renamed = True
                        except Exception as e:
                            log_to_dialog(f"❌ Erreur renommage: {e}")
                    else:
                        log_to_dialog("⏭️ Renommage annulé")

                step_label.configure(text="✅ Configuration terminée!")
                log_to_dialog("=" * 50)
                log_to_dialog("✅ AUTO SETUP POSTE STANDARD TERMINÉ!")

                # Proposer redémarrage si PC renommé
                if pc_renamed:
                    dialog.update()
                    if messagebox.askyesno(
                            "Redémarrage requis",
                            "Le PC a été renommé.\n\nVoulez-vous redémarrer maintenant ?",
                            parent=dialog):
                        log_to_dialog(
                            "🔄 Redémarrage du système dans 10 secondes...")
                        subprocess.run("shutdown /r /t 10", shell=True)
                        log_to_dialog("✅ Redémarrage planifié")
                    else:
                        log_to_dialog(
                            "⚠️ Redémarrez manuellement pour appliquer le nouveau nom"
                        )

            elif setup_type == "serveur":
                step_label.configure(text="⚠️ Configuration en attente")
                log_to_dialog(
                    "⚠️ Poste Serveur: Configuration en attente de définition")
                log_to_dialog("Aucune action configurée pour le moment.")
                progress_bar.set(1.0)

            elif setup_type == "veloce":
                # Utiliser les paramètres passés
                server = server_name
                station = station_number

                # Formater le numéro de station (01, 02, etc.)
                station_formatted = f"{station:02d}"
                station_no_zero = str(station)

                log_to_dialog(f"Serveur: {server}")
                log_to_dialog(
                    f"Numéro de station: {station} (formaté: {station_formatted})"
                )
                progress_bar.set(0.1)

                # Chemins
                veloce_base = f"\\\\{server}\\veloce"
                station_folder = f"stat{station_formatted}"
                station_path = os.path.join(veloce_base, station_folder,
                                            "install")
                install_exe = os.path.join(
                    station_path, f"install (WS{station_formatted}).exe")
                ws_starter = os.path.join(station_path,
                                          f"WS Starter{station_no_zero}.exe")
                desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                appdata = os.getenv("APPDATA") or os.path.expanduser("~")
                startup_folder = os.path.join(appdata, "Microsoft", "Windows",
                                              "Start Menu", "Programs",
                                              "Startup")

                # Étape 1: Vérifier l'accès au serveur
                step_label.configure(text="Vérification accès réseau...")
                log_to_dialog(f"▶ Vérification accès à {veloce_base}...")

                try:
                    import subprocess
                    ping_result = subprocess.run(f"ping -n 1 -w 1000 {server}",
                                                 shell=True,
                                                 capture_output=True,
                                                 timeout=2)

                    if ping_result.returncode != 0:
                        log_to_dialog(f"❌ Serveur {server} non joignable")
                        step_label.configure(text="❌ Serveur non joignable")
                        progress_bar.set(1.0)
                        return

                    log_to_dialog(f"✓ Serveur {server} joignable")

                    if not os.path.exists(station_path):
                        log_to_dialog(
                            f"❌ Dossier {station_folder} introuvable")
                        log_to_dialog(f"Chemin: {station_path}")
                        step_label.configure(
                            text="❌ Dossier station introuvable")
                        progress_bar.set(1.0)
                        return

                    log_to_dialog(
                        f"✓ Dossier station accessible: {station_path}")
                    progress_bar.set(0.2)

                except Exception as e:
                    log_to_dialog(f"❌ Erreur réseau: {e}")
                    step_label.configure(text="❌ Erreur réseau")
                    progress_bar.set(1.0)
                    return

                # Étape 2: Installer install (WSXX).exe en mode admin
                step_label.configure(text="Installation de l'application...")
                log_to_dialog(
                    f"▶ Lancement de install (WS{station_formatted}).exe en mode admin..."
                )

                try:
                    if not os.path.exists(install_exe):
                        log_to_dialog(f"❌ Fichier introuvable: {install_exe}")
                        step_label.configure(
                            text="❌ Fichier install introuvable")
                        progress_bar.set(1.0)
                        return

                    import ctypes
                    # Lancer en mode admin avec le bon répertoire de travail
                    ret = ctypes.windll.shell32.ShellExecuteW(
                        None, "runas", install_exe, None, station_path, 1)

                    if ret > 32:
                        log_to_dialog(
                            f"✓ install (WS{station_formatted}).exe lancé avec succès"
                        )
                    else:
                        log_to_dialog(f"❌ Échec du lancement (code: {ret})")
                        step_label.configure(text="❌ Erreur installation")
                        progress_bar.set(1.0)
                        return

                    progress_bar.set(0.4)
                    time.sleep(1)

                except Exception as e:
                    log_to_dialog(f"❌ Erreur lors de l'installation: {e}")
                    step_label.configure(text="❌ Erreur installation")
                    progress_bar.set(1.0)
                    return

                # Étape 3: Créer raccourci sur le bureau
                step_label.configure(text="Création du raccourci bureau...")
                log_to_dialog(
                    f"▶ Création du raccourci 'station {station_no_zero}' sur le bureau..."
                )

                try:
                    if not os.path.exists(ws_starter):
                        log_to_dialog(
                            f"❌ Fichier source introuvable: {ws_starter}")
                        step_label.configure(text="❌ WS Starter introuvable")
                        progress_bar.set(1.0)
                        return

                    # Utiliser PowerShell pour créer le raccourci
                    shortcut_path = os.path.join(
                        desktop, f"station {station_no_zero}.lnk")
                    ps_script = f'''
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{ws_starter}"
$Shortcut.WorkingDirectory = "{station_path}"
$Shortcut.Save()
'''
                    ps_cmd = [
                        'powershell', '-ExecutionPolicy', 'Bypass', '-Command',
                        ps_script
                    ]
                    result = subprocess.run(ps_cmd,
                                            capture_output=True,
                                            text=True)

                    if result.returncode == 0 and os.path.exists(
                            shortcut_path):
                        log_to_dialog(f"✓ Raccourci créé: {shortcut_path}")
                    else:
                        log_to_dialog(
                            f"❌ Erreur création raccourci: {result.stderr}")
                        log_to_dialog("⚠️ Continuez manuellement...")

                    progress_bar.set(0.6)

                except Exception as e:
                    log_to_dialog(f"❌ Erreur création raccourci: {e}")
                    log_to_dialog("⚠️ Continuez manuellement...")

                # Étape 4: Appliquer clé de registre
                step_label.configure(
                    text="Application de la clé de registre...")
                log_to_dialog(
                    "▶ Application de la clé de registre DirectoryCacheLifetime..."
                )

                try:
                    reg_cmd = r'C:\Windows\System32\reg.exe add HKLM\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters /v DirectoryCacheLifetime /t REG_DWORD /d 0 /f'
                    result = subprocess.run(reg_cmd,
                                            shell=True,
                                            capture_output=True,
                                            text=True)

                    if result.returncode == 0:
                        log_to_dialog(
                            "✓ Clé de registre appliquée avec succès")
                    else:
                        log_to_dialog(f"❌ Erreur registre: {result.stderr}")

                    progress_bar.set(0.8)

                except Exception as e:
                    log_to_dialog(f"❌ Erreur clé registre: {e}")

                # Étape 5: Copier raccourci dans le démarrage
                step_label.configure(
                    text="Configuration du démarrage automatique...")
                log_to_dialog(
                    "▶ Copie du raccourci dans le dossier de démarrage...")

                try:
                    shortcut_source = os.path.join(
                        desktop, f"station {station_no_zero}.lnk")
                    shortcut_dest = os.path.join(
                        startup_folder, f"station {station_no_zero}.lnk")

                    if os.path.exists(shortcut_source):
                        import shutil
                        shutil.copy2(shortcut_source, shortcut_dest)
                        log_to_dialog(f"✓ Raccourci copié dans Démarrage")
                    else:
                        log_to_dialog(
                            "⚠️ Raccourci source introuvable pour copie")

                    # Supprimer l'ancien raccourci Veloce WS Starter.exe
                    old_shortcut = os.path.join(startup_folder,
                                                "Veloce WS Starter.exe")
                    if os.path.exists(old_shortcut):
                        os.remove(old_shortcut)
                        log_to_dialog(
                            "✓ Ancien raccourci 'Veloce WS Starter.exe' supprimé"
                        )

                    progress_bar.set(1.0)
                    step_label.configure(text="✅ Configuration terminée!")
                    log_to_dialog("=" * 50)
                    log_to_dialog("✅ STATION VELOCE CONFIGURÉE AVEC SUCCÈS!")

                except Exception as e:
                    log_to_dialog(f"⚠️ Erreur démarrage automatique: {e}")
                    log_to_dialog(
                        "Configuration principale terminée, vérifiez manuellement le démarrage"
                    )
                    progress_bar.set(1.0)
                    step_label.configure(
                        text="✅ Configuration terminée (avec avertissements)")

            log_to_dialog("=" * 50)

        # Bouton démarrer
        def start_setup():
            """Démarre le setup après avoir demandé les paramètres si nécessaire"""
            server = None
            station_num = None
            if setup_type == "veloce":
                # Demander le serveur réseau AVANT de lancer le thread
                from tkinter import simpledialog
                server = simpledialog.askstring(
                    "Serveur réseau",
                    "Nom du serveur réseau (ex: SV):",
                    initialvalue="SV",
                    parent=dialog)

                if not server:
                    log_to_dialog("❌ Configuration annulée")
                    progress_bar.set(1.0)
                    return

                # Demander le numéro de station
                station_str = simpledialog.askstring(
                    "Numéro de station",
                    "Numéro de la station (ex: 1, 2, 3...):",
                    parent=dialog)

                if not station_str:
                    log_to_dialog("❌ Configuration annulée")
                    progress_bar.set(1.0)
                    return

                try:
                    station_num = int(station_str)
                    if station_num < 1:
                        raise ValueError("Numéro invalide")
                except:
                    log_to_dialog("❌ Numéro de station invalide")
                    progress_bar.set(1.0)
                    return

            # Lancer le worker avec les paramètres
            threading.Thread(target=lambda: run_worker(server, station_num),
                             daemon=True).start()

        ctk.CTkButton(main_frame,
                      text="🚀 Démarrer",
                      command=start_setup,
                      fg_color="#16a34a",
                      hover_color="#15803d").pack(pady=10)

        # Bouton fermer
        ctk.CTkButton(main_frame,
                      text="Fermer",
                      command=dialog.destroy,
                      fg_color="#dc2626",
                      hover_color="#b91c1c").pack(pady=5)

    def build_custom_commands_options(self, parent):
        """Page Commandes personnalisées avec support PsExec"""
        f = ctk.CTkScrollableFrame(parent)
        f.pack(fill="both", expand=True, padx=6, pady=6)

        ctk.CTkLabel(f,
                     text="Commandes personnalisées (Local ou Distant)",
                     font=ctk.CTkFont(size=16,
                                      weight="bold")).pack(anchor="w",
                                                           pady=(0, 10))

        # Variables pour les champs
        if not hasattr(self, 'psexec_host_var'):
            self.psexec_host_var = tk.StringVar(value="")
            self.psexec_user_var = tk.StringVar(value="")
            self.psexec_pass_var = tk.StringVar(value="")
            self.psexec_cmd_var = tk.StringVar(value="")

        # Champs de saisie
        fields_frame = ctk.CTkFrame(f)
        fields_frame.pack(fill="x", pady=8)

        # Hôte cible (optionnel)
        ctk.CTkLabel(fields_frame,
                     text="Hôte distant (optionnel):").grid(row=0,
                                                            column=0,
                                                            sticky="w",
                                                            padx=10,
                                                            pady=5)
        host_entry = ctk.CTkEntry(fields_frame,
                                  textvariable=self.psexec_host_var,
                                  width=300,
                                  placeholder_text="Vide = local")
        host_entry.grid(row=0, column=1, padx=10, pady=5)

        # Utilisateur (optionnel)
        ctk.CTkLabel(fields_frame,
                     text="Utilisateur distant:").grid(row=1,
                                                       column=0,
                                                       sticky="w",
                                                       padx=10,
                                                       pady=5)
        ctk.CTkEntry(fields_frame,
                     textvariable=self.psexec_user_var,
                     width=300,
                     placeholder_text="Optionnel").grid(row=1,
                                                        column=1,
                                                        padx=10,
                                                        pady=5)

        # Mot de passe (optionnel)
        ctk.CTkLabel(fields_frame,
                     text="Mot de passe distant:").grid(row=2,
                                                        column=0,
                                                        sticky="w",
                                                        padx=10,
                                                        pady=5)
        ctk.CTkEntry(fields_frame,
                     textvariable=self.psexec_pass_var,
                     width=300,
                     show="*",
                     placeholder_text="Optionnel").grid(row=2,
                                                        column=1,
                                                        padx=10,
                                                        pady=5)

        # Commande
        ctk.CTkLabel(fields_frame,
                     text="Commande à exécuter:").grid(row=3,
                                                       column=0,
                                                       sticky="w",
                                                       padx=10,
                                                       pady=5)
        ctk.CTkEntry(fields_frame, textvariable=self.psexec_cmd_var,
                     width=400).grid(row=3, column=1, padx=10, pady=5)

        # Bouton exécuter
        ctk.CTkButton(f,
                      text="🚀 Exécuter la commande",
                      width=200,
                      command=self._run_custom_command,
                      fg_color="#2b6ee6",
                      hover_color="#2058c9").pack(pady=10)

        # Commandes rapides
        quick_frame = ctk.CTkFrame(f)
        quick_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkLabel(quick_frame,
                     text="⚡ Commandes rapides:",
                     font=ctk.CTkFont(size=13,
                                      weight="bold")).pack(anchor="w",
                                                           padx=10,
                                                           pady=(10, 5))

        quick_commands = [
            ("Informations système", "systeminfo"),
            ("Liste processus", "tasklist"),
            ("Redémarrer", "shutdown /r /t 0"),
            ("Ouvrir CMD", "cmd.exe"),
        ]

        btn_grid = ctk.CTkFrame(quick_frame, fg_color="transparent")
        btn_grid.pack(fill="x", padx=10, pady=5)

        for idx, (name, cmd) in enumerate(quick_commands):
            row = idx // 2
            col = idx % 2
            ctk.CTkButton(
                btn_grid,
                text=name,
                width=180,
                command=lambda c=cmd: self.psexec_cmd_var.set(c)).grid(
                    row=row, column=col, padx=5, pady=5)

        # Note importante
        note_frame = ctk.CTkFrame(f, fg_color="#3a3a3a")
        note_frame.pack(fill="x", pady=(10, 0), padx=10)

        note_text = """
ℹ️ MODE D'EMPLOI:
• Local: Laisser "Hôte distant" vide → exécution locale
• Distant: Renseigner IP/nom + credentials → exécution via PsExec
  (PsExec doit être dans config/psexec.exe)
  Télécharger: https://learn.microsoft.com/sysinternals/downloads/psexec
"""
        ctk.CTkLabel(note_frame,
                     text=note_text,
                     justify="left",
                     text_color="#a5d6ff",
                     font=ctk.CTkFont(size=11)).pack(padx=15, pady=10)

    def _run_custom_command(self):
        """Exécute une commande (locale ou distante via PsExec)"""
        host = self.psexec_host_var.get().strip()
        user = self.psexec_user_var.get().strip()
        password = self.psexec_pass_var.get().strip()
        command = self.psexec_cmd_var.get().strip()

        if not command:
            self.log("❌ Commande requise")
            return

        def worker():
            try:
                # Mode LOCAL (host vide)
                if not host:
                    self.log(f"▶ Exécution LOCALE: {command}")
                    result = subprocess.run(command,
                                            shell=True,
                                            capture_output=True,
                                            text=True,
                                            timeout=60)

                    if result.stdout:
                        self.log("----- SORTIE -----")
                        for line in result.stdout.splitlines():
                            self.log(line)

                    if result.stderr:
                        self.log("----- ERREURS -----")
                        for line in result.stderr.splitlines():
                            self.log(line)

                    self.log(
                        f"✅ Commande locale terminée (code: {result.returncode})"
                    )
                    return

                # Mode DISTANT (avec PsExec)
                base_path = get_base_path()
                psexec_path = os.path.join(base_path, "config", "psexec.exe")

                if not os.path.exists(psexec_path):
                    self.log(f"❌ PsExec introuvable: {psexec_path}")
                    self.log(
                        "📥 Téléchargez PsExec et placez-le dans config/psexec.exe"
                    )
                    return

                # Construction de la commande PsExec
                cmd_parts = [psexec_path, f"\\\\{host}"]
                if user:
                    cmd_parts.extend(["-u", user])
                if password:
                    cmd_parts.extend(["-p", password])

                cmd_parts.extend(["-accepteula", command])

                self.log(f"▶ Exécution DISTANTE sur {host}: {command}")

                result = subprocess.run(cmd_parts,
                                        capture_output=True,
                                        text=True,
                                        timeout=60)

                if result.stdout:
                    self.log("----- SORTIE -----")
                    for line in result.stdout.splitlines():
                        self.log(line)

                if result.stderr:
                    self.log("----- ERREURS -----")
                    for line in result.stderr.splitlines():
                        self.log(line)

                self.log(
                    f"✅ Commande distante terminée (code: {result.returncode})"
                )

            except subprocess.TimeoutExpired:
                self.log("❌ Timeout: La commande a pris trop de temps")
            except Exception as e:
                self.log(f"❌ Erreur: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def build_ip_config_options(self, parent):
        """Page configuration IP réseau complète - Style Windows"""
        f = ctk.CTkScrollableFrame(parent)
        f.pack(fill="both", expand=True, padx=10, pady=10)

        # Titre
        ctk.CTkLabel(f,
                     text="Propriétés de : Protocole Internet version 4 (TCP/IPv4)",
                     font=ctk.CTkFont(size=15,
                                      weight="bold")).pack(anchor="w",
                                                           pady=(0, 15))

        # Variables
        if not hasattr(self, '_net_iface_var'):
            self._net_iface_var = tk.StringVar(value="")
            self._net_ip_var = tk.StringVar(value="")
            self._net_mask_var = tk.StringVar(value="")
            self._net_gw_var = tk.StringVar(value="")
            self._net_dns1_var = tk.StringVar(value="")
            self._net_dns2_var = tk.StringVar(value="")
            self._net_ip_mode_var = tk.StringVar(value="dhcp")  # dhcp ou static
            self._net_dns_mode_var = tk.StringVar(value="dhcp")  # dhcp ou static
            self._net_ifaces_info = {}

        # ========== Sélection Interface ==========
        iface_frame = ctk.CTkFrame(f, fg_color="#2b2b2b")
        iface_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(iface_frame, text="🌐 Carte réseau :", 
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))

        inner_frame = ctk.CTkFrame(iface_frame, fg_color="transparent")
        inner_frame.pack(fill="x", padx=15, pady=(0, 10))

        self._iface_menu = ctk.CTkOptionMenu(inner_frame,
                                             variable=self._net_iface_var,
                                             values=[],
                                             width=450)
        self._iface_menu.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            inner_frame,
            text="🔄 Recharger",
            width=100,
            command=lambda: threading.Thread(target=self._detect_interfaces,
                                             daemon=True).start()).pack(side="left", padx=(0, 8))

        # Bouton pour ouvrir directement les propriétés IPv4 Windows
        ctk.CTkButton(
            inner_frame,
            text="🔧 Ouvrir propriétés IPv4 Windows",
            width=220,
            fg_color="#10b981",
            hover_color="#059669",
            command=self._open_ipv4_properties).pack(side="left")

        # ========== CONFIGURATION IP ==========
        ip_section = ctk.CTkFrame(f, fg_color="#2b2b2b")
        ip_section.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(ip_section, 
                     text="Les paramètres IP peuvent être déterminés automatiquement si votre réseau le permet.",
                     text_color="#9ca3af",
                     font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15, pady=(12, 8))

        # Radio DHCP IP
        ctk.CTkRadioButton(ip_section,
                           text="○ Obtenir automatiquement une adresse IP",
                           variable=self._net_ip_mode_var,
                           value="dhcp",
                           font=ctk.CTkFont(size=12)).pack(anchor="w", padx=15, pady=4)

        # Radio IP Manuelle
        ctk.CTkRadioButton(ip_section,
                           text="● Utiliser l'adresse IP suivante :",
                           variable=self._net_ip_mode_var,
                           value="static",
                           font=ctk.CTkFont(size=12)).pack(anchor="w", padx=15, pady=(8, 8))

        # Champs IP
        fields_frame = ctk.CTkFrame(ip_section, fg_color="transparent")
        fields_frame.pack(fill="x", padx=40, pady=(0, 12))

        def create_ip_field(parent, label_text, var):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=label_text, width=180,
                         anchor="w").pack(side="left")
            entry = ctk.CTkEntry(row, textvariable=var, width=250)
            entry.pack(side="left", padx=5)
            return entry

        self._net_ip_entry = create_ip_field(fields_frame, "Adresse IP :", self._net_ip_var)
        self._net_mask_entry = create_ip_field(fields_frame, "Masque de sous-réseau :", self._net_mask_var)
        self._net_gw_entry = create_ip_field(fields_frame, "Passerelle par défaut :", self._net_gw_var)

        # ========== CONFIGURATION DNS ==========
        dns_section = ctk.CTkFrame(f, fg_color="#2b2b2b")
        dns_section.pack(fill="x", pady=(0, 15))

        # Radio DHCP DNS
        ctk.CTkRadioButton(dns_section,
                           text="○ Obtenir automatiquement les adresses des serveurs DNS",
                           variable=self._net_dns_mode_var,
                           value="dhcp",
                           font=ctk.CTkFont(size=12)).pack(anchor="w", padx=15, pady=(12, 4))

        # Radio DNS Manuel
        ctk.CTkRadioButton(dns_section,
                           text="● Utiliser l'adresse de serveur DNS suivante :",
                           variable=self._net_dns_mode_var,
                           value="static",
                           font=ctk.CTkFont(size=12)).pack(anchor="w", padx=15, pady=(8, 8))

        # Champs DNS
        dns_fields_frame = ctk.CTkFrame(dns_section, fg_color="transparent")
        dns_fields_frame.pack(fill="x", padx=40, pady=(0, 12))

        self._net_dns1_entry = create_ip_field(dns_fields_frame, "Serveur DNS préféré :", self._net_dns1_var)
        self._net_dns2_entry = create_ip_field(dns_fields_frame, "Serveur DNS auxiliaire :", self._net_dns2_var)

        # ========== BOUTON APPLIQUER ==========
        ctk.CTkButton(
            f,
            text="✅ OK - Appliquer la configuration",
            width=280,
            height=40,
            fg_color="#2b6ee6",
            hover_color="#2058c9",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: threading.Thread(target=self._apply_network_config,
                                             daemon=True).start()).pack(pady=(5, 10))

        # Activer/Désactiver champs selon mode
        def toggle_ip_fields(*args):
            state = "normal" if self._net_ip_mode_var.get() == "static" else "disabled"
            for entry in [self._net_ip_entry, self._net_mask_entry, self._net_gw_entry]:
                entry.configure(state=state)

        def toggle_dns_fields(*args):
            state = "normal" if self._net_dns_mode_var.get() == "static" else "disabled"
            for entry in [self._net_dns1_entry, self._net_dns2_entry]:
                entry.configure(state=state)

        self._net_ip_mode_var.trace_add("write", toggle_ip_fields)
        self._net_dns_mode_var.trace_add("write", toggle_dns_fields)
        toggle_ip_fields()
        toggle_dns_fields()

        # Remplir les champs quand on change d'interface
        def on_iface_change(iface_name):
            info = self._net_ifaces_info.get(iface_name, {})

            # D'abord mettre en mode static pour activer les champs et afficher les valeurs actuelles
            self._net_ip_mode_var.set("static")
            self._net_dns_mode_var.set("static")

            # Remplir tous les champs avec les valeurs actuelles (même si DHCP)
            self._net_ip_var.set(info.get("ip", ""))
            self._net_mask_var.set(info.get("mask", ""))
            self._net_gw_var.set(info.get("gw", ""))
            self._net_dns1_var.set(info.get("dns1", ""))
            self._net_dns2_var.set(info.get("dns2", ""))

            # Ensuite déterminer le vrai mode selon la configuration
            ip_is_dhcp = info.get("dhcp", True)
            # Ne mettre en DHCP que si c'est vraiment configuré en DHCP
            # Sinon laisser en static pour que l'utilisateur voie les valeurs actuelles
            if ip_is_dhcp:
                self._net_ip_mode_var.set("dhcp")

            # DNS auto si vide ET IP est en DHCP
            dns_is_auto = (not info.get("dns1", "") and not info.get("dns2", "")) and ip_is_dhcp
            if dns_is_auto:
                self._net_dns_mode_var.set("dhcp")

            # Logger les infos pour debug
            self.log(f"📊 Carte: {iface_name}")
            self.log(f"   IP: {info.get('ip', 'N/A')} - Mode: {'DHCP' if ip_is_dhcp else 'Static'}")
            self.log(f"   Masque: {info.get('mask', 'N/A')}")
            self.log(f"   Passerelle: {info.get('gw', 'Aucune')}")
            self.log(f"   DNS: {info.get('dns1', 'N/A')} / {info.get('dns2', 'N/A')}")
            self.log("")

        self._iface_menu.configure(command=lambda v: on_iface_change(v))

        # Lancer la détection au démarrage
        threading.Thread(target=self._detect_interfaces, daemon=True).start()

    def _detect_interfaces(self):
        """Détecte les interfaces réseau et récupère leurs configs"""
        try:
            self.log("▶ Détection des interfaces réseau...")

            # Liste des interfaces via psutil
            interfaces = list(psutil.net_if_addrs().keys())
            infos = {}

            for iface in interfaces:
                try:
                    # Récupère les infos via netsh
                    result = subprocess.check_output(
                        f'netsh interface ip show config name="{iface}"',
                        shell=True,
                        text=True,
                        encoding="utf-8",
                        errors="ignore")

                    # Parse la sortie
                    info = self._parse_netsh_output(result)
                    dns_list = info.get("dns", [])

                    infos[iface] = {
                        "ip": info.get("ip", ""),
                        "mask": info.get("mask", ""),
                        "gw": info.get("gateway", ""),
                        "dns1": dns_list[0] if len(dns_list) > 0 else "",
                        "dns2": dns_list[1] if len(dns_list) > 1 else "",
                        "dhcp": info.get("dhcp", True)
                    }
                except:
                    infos[iface] = {
                        "ip": "",
                        "mask": "",
                        "gw": "",
                        "dns1": "",
                        "dns2": "",
                        "dhcp": True
                    }

            # Mettre à jour l'UI
            def update_ui():
                self._net_ifaces_info = infos
                names = list(infos.keys())

                if names:
                    self._iface_menu.configure(values=names)
                    current = self._net_iface_var.get()
                    selected = current if current in names else names[0]
                    self._net_iface_var.set(selected)

                    # Remplir les champs
                    info = infos[selected]
                    self._net_ip_var.set(info["ip"])
                    self._net_mask_var.set(info["mask"])
                    self._net_gw_var.set(info["gw"])
                    self._net_dns1_var.set(info["dns1"])
                    self._net_dns2_var.set(info["dns2"])
                    self._net_mode_var.set(
                        "dhcp" if info["dhcp"] else "static")
                else:
                    self._iface_menu.configure(values=["Aucune interface"])
                    self._net_iface_var.set("")

                self.log(f"✅ {len(names)} interface(s) détectée(s)")

            self.after(0, update_ui)

        except Exception as e:
            self.log(f"❌ Erreur détection interfaces: {e}")

    def _parse_netsh_output(self, output):
        """Parse la sortie de netsh pour extraire les infos réseau"""
        info = {"ip": "", "mask": "", "gateway": "", "dns": [], "dhcp": True}

        # Détecter DHCP vs Static - regarder plusieurs patterns
        dhcp_match = re.search(
            r"DHCP\s+(?:activé|enabled)\s*:\s*(Oui|Yes|Non|No)", output,
            re.IGNORECASE | re.MULTILINE)
        if dhcp_match:
            dhcp_value = dhcp_match.group(1).lower()
            info["dhcp"] = dhcp_value in ["oui", "yes"]
        else:
            # Si pas de ligne DHCP trouvée, chercher "statically configured" ou "configured statically"
            if re.search(r"(?:statically|statique)", output, re.IGNORECASE):
                info["dhcp"] = False
            elif re.search(r"(?:dhcp|dynamique)", output, re.IGNORECASE):
                info["dhcp"] = True

        lines = output.splitlines()

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # IP Address - cherche plusieurs patterns
            if any(x in line_lower for x in ["adresse ip", "ip address"]):
                # Sur la même ligne
                m = re.search(r":\s*([\d\.]+)", line)
                if m and m.group(1) != "0.0.0.0":
                    info["ip"] = m.group(1)
                # Ligne suivante
                elif i + 1 < len(lines):
                    m = re.search(r"([\d\.]+)", lines[i + 1])
                    if m and m.group(1) != "0.0.0.0":
                        info["ip"] = m.group(1)

            # Subnet Mask - cherche plusieurs patterns
            if any(x in line_lower for x in
                   ["masque de sous", "subnet mask", "subnet prefix"]):
                # Format direct 255.255.255.0
                m = re.search(r":\s*([\d\.]+)", line)
                if m:
                    info["mask"] = m.group(1)
                # Format CIDR /24
                elif "/" in line:
                    m = re.search(r"/(\d+)", line)
                    if m:
                        prefix = int(m.group(1))
                        mask_bits = '1' * prefix + '0' * (32 - prefix)
                        octets = [
                            str(int(mask_bits[i:i + 8], 2))
                            for i in range(0, 32, 8)
                        ]
                        info["mask"] = '.'.join(octets)
                # Ligne suivante
                elif i + 1 < len(lines):
                    m = re.search(r"([\d\.]+)", lines[i + 1])
                    if m:
                        info["mask"] = m.group(1)

            # Gateway - cherche plusieurs patterns
            if any(x in line_lower
                   for x in ["passerelle", "gateway", "default gateway"]):
                # Sur la même ligne
                m = re.search(r":\s*([\d\.]+)", line)
                if m and m.group(1) not in ["0.0.0.0", ""]:
                    info["gateway"] = m.group(1)
                # Ligne suivante
                elif i + 1 < len(lines):
                    m = re.search(r"([\d\.]+)", lines[i + 1])
                    if m and m.group(1) not in ["0.0.0.0", ""]:
                        info["gateway"] = m.group(1)

            # DNS Servers
            if any(x in line_lower for x in ["serveur dns", "dns server"]):
                # Sur la même ligne
                m = re.search(r":\s*([\d\.]+)", line)
                if m:
                    info["dns"].append(m.group(1))
                # Lignes suivantes (DNS multiples)
                j = i + 1
                while j < len(lines) and j < i + 5:
                    m = re.search(r"^\s*([\d\.]+)\s*$", lines[j].strip())
                    if m:
                        info["dns"].append(m.group(1))
                        j += 1
                    else:
                        break

        return info

    def _open_ipv4_properties(self):
        """Ouvre les propriétés IPv4 Windows de la carte réseau sélectionnée"""
        try:
            iface_name = self._net_iface_var.get()

            if not iface_name:
                self.log("❌ Aucune interface sélectionnée")
                self.log("   Veuillez d'abord sélectionner une carte réseau")
                return

            self.log(f"▶ Ouverture des propriétés réseau pour: {iface_name}")
            self.log("")

            # Ouvrir le panneau de configuration réseau (Network Connections)
            subprocess.Popen('control ncpa.cpl', shell=True)

            self.log("✓ Panneau Connexions réseau Windows ouvert")
            self.log("")
            self.log(f"🎯 CARTE SÉLECTIONNÉE: {iface_name}")
            self.log("")
            self.log("📋 Instructions rapides:")
            self.log(f"   1. Chercher la carte: {iface_name}")
            self.log("   2. Clic DROIT sur cette carte → Propriétés")
            self.log("   3. Double-clic sur: 'Protocole Internet version 4 (TCP/IPv4)'")
            self.log("   4. Configurer l'adresse IP, masque, passerelle et DNS")
            self.log("   5. Cliquer 'OK' pour enregistrer")
            self.log("")

            # Afficher les infos actuelles de la carte pour référence
            info = self._net_ifaces_info.get(iface_name, {})
            if info and info.get("ip"):
                self.log("📊 Configuration actuelle de cette carte:")
                self.log(f"   IP: {info.get('ip', 'N/A')}")
                self.log(f"   Masque: {info.get('mask', 'N/A')}")
                self.log(f"   Passerelle: {info.get('gw', 'N/A')}")
                self.log(f"   DNS primaire: {info.get('dns1', 'N/A')}")
                self.log(f"   DNS secondaire: {info.get('dns2', 'N/A')}")
                self.log("")

        except Exception as e:
            self.log(f"❌ Erreur ouverture propriétés réseau: {e}")

    def _apply_network_config(self):
        """Applique la configuration réseau (IP et DNS séparés)"""
        iface = self._net_iface_var.get()
        if not iface:
            self.log("❌ Aucune interface sélectionnée")
            return

        if not is_admin():
            self.log("🔼 Droits administrateur requis, relance...")
            try:
                relaunch_as_admin()
            except Exception as e:
                self.log(f"❌ Impossible de relancer en admin: {e}")
            return

        ip_mode = self._net_ip_mode_var.get()
        dns_mode = self._net_dns_mode_var.get()

        self.log(f"▶ Application de la configuration sur '{iface}'")
        self.log(f"  Mode IP: {ip_mode}, Mode DNS: {dns_mode}")

        try:
            # ===== CONFIGURATION IP =====
            if ip_mode == "dhcp":
                subprocess.run(
                    f'netsh interface ip set address name="{iface}" source=dhcp',
                    shell=True,
                    check=True)
                self.log("✅ Adresse IP configurée en DHCP (automatique)")
            else:
                # IP statique
                ip = self._net_ip_var.get().strip()
                mask = self._net_mask_var.get().strip()
                gw = self._net_gw_var.get().strip()

                if not ip or not mask:
                    self.log("❌ IP et masque requis pour IP statique")
                    return

                # netsh nécessite un argument gateway même s'il est vide (utiliser "none")
                gateway_arg = gw if gw else "none"
                cmd = f'netsh interface ip set address name="{iface}" static {ip} {mask} {gateway_arg}'

                subprocess.run(cmd, shell=True, check=True)
                self.log(f"✅ IP statique configurée: {ip}/{mask}")
                if gw:
                    self.log(f"✅ Passerelle: {gw}")
                else:
                    self.log("✅ Passerelle: aucune")

            # ===== CONFIGURATION DNS =====
            if dns_mode == "dhcp":
                subprocess.run(
                    f'netsh interface ip set dns name="{iface}" source=dhcp',
                    shell=True,
                    check=True)
                self.log("✅ DNS configuré en automatique")
            else:
                # DNS manuel
                dns1 = self._net_dns1_var.get().strip()
                dns2 = self._net_dns2_var.get().strip()

                if dns1:
                    subprocess.run(
                        f'netsh interface ip set dns name="{iface}" static {dns1}',
                        shell=True,
                        check=True)
                    self.log(f"✅ DNS primaire: {dns1}")

                if dns2:
                    subprocess.run(
                        f'netsh interface ip add dns name="{iface}" {dns2}',
                        shell=True,
                        check=True)
                    self.log(f"✅ DNS secondaire: {dns2}")

            time.sleep(1)
            self.log("🔄 Actualisation des informations...")
            self._detect_interfaces()

        except Exception as e:
            self.log(f"❌ Erreur: {e}")

    # ==================== SYSTÈME DE MISE À JOUR ====================

    def _check_updates_auto(self):
        """Vérification automatique des mises à jour au démarrage (discrète)"""
        try:
            time.sleep(2)  # Attendre que l'interface soit chargée

            update_available, local_ver, remote_ver = check_for_updates()

            if remote_ver:
                # Mettre à jour le label de version
                version_text = f"Version {remote_ver}"
                if update_available:
                    version_text += " 🔴 Mise à jour disponible!"

                self.after(0, lambda: self.version_label.configure(
                    text=version_text,
                    text_color="#ef4444" if update_available else None))

                # Afficher notification dans la console
                if update_available:
                    self.after(0, lambda: self.log(
                        f"🔔 Nouvelle version disponible: {remote_ver} (installée: {local_ver})"))
                    self.after(0, lambda: self.log(
                        "   Cliquez sur '🔄 Vérifier mises à jour' pour télécharger"))
        except Exception as e:
            print(f"Erreur vérification auto: {e}")

    def _check_updates_manual(self):
        """Vérification manuelle des mises à jour (avec popup)"""
        self.log("🔍 Vérification des mises à jour...")

        def worker():
            try:
                update_available, local_ver, remote_ver = check_for_updates()

                if not remote_ver:
                    self.after(0, lambda: self.log(
                        "❌ Impossible de contacter le serveur de mises à jour"))
                    self.after(0, lambda: messagebox.showerror(
                        "Erreur",
                        "Impossible de vérifier les mises à jour.\n"
                        "Vérifiez votre connexion Internet."))
                    return

                if update_available:
                    self.after(0, lambda: self.log(
                        f"✅ Mise à jour disponible: v{remote_ver} (actuelle: v{local_ver})"))
                    self.after(0, lambda: self._show_update_dialog(local_ver, remote_ver))
                else:
                    self.after(0, lambda: self.log(
                        f"✅ Vous avez la dernière version: v{local_ver}"))
                    self.after(0, lambda: messagebox.showinfo(
                        "Aucune mise à jour",
                        f"Vous utilisez déjà la dernière version:\nVersion {local_ver}"))

            except Exception as e:
                self.after(0, lambda: self.log(f"❌ Erreur: {e}"))
                self.after(0, lambda: messagebox.showerror("Erreur", str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _show_update_dialog(self, current_version, new_version):
        """Affiche le dialogue de mise à jour"""
        from tkinter import Toplevel

        dialog = Toplevel(self)
        dialog.title("Mise à jour disponible")
        dialog.geometry("550x600")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Centrer la fenêtre
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f"+{x}+{y}")

        # Icône
        try:
            base_path = get_base_path()
            icon_path = os.path.join(base_path, "mainicon.ico")
            if os.path.exists(icon_path):
                dialog.iconbitmap(icon_path)
        except:
            pass

        # Contenu
        main_frame = ctk.CTkFrame(dialog, fg_color="#1e1e1e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Icône de mise à jour
        ctk.CTkLabel(main_frame,
                     text="🔄",
                     font=ctk.CTkFont(size=48)).pack(pady=(10, 5))

        # Titre
        ctk.CTkLabel(main_frame,
                     text="Mise à jour disponible !",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)

        # Versions
        version_frame = ctk.CTkFrame(main_frame, fg_color="#2b2b2b")
        version_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(version_frame,
                     text=f"Version actuelle: {current_version}",
                     font=ctk.CTkFont(size=13),
                     text_color="#9ca3af").pack(pady=5)

        ctk.CTkLabel(version_frame,
                     text=f"Nouvelle version: {new_version}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#10b981").pack(pady=5)

        # Message
        ctk.CTkLabel(main_frame,
                     text="Voulez-vous télécharger et installer\ncette mise à jour maintenant ?",
                     font=ctk.CTkFont(size=12),
                     text_color="#d1d5db").pack(pady=10)

        # Boutons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame,
                      text="✅ Télécharger et installer",
                      width=200,
                      height=35,
                      command=lambda: [dialog.destroy(), 
                                      self._download_and_install_update()],
                      fg_color="#16a34a",
                      hover_color="#15803d",
                      font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame,
                      text="❌ Plus tard",
                      width=120,
                      height=35,
                      command=dialog.destroy,
                      fg_color="#6b7280",
                      hover_color="#4b5563",
                      font=ctk.CTkFont(size=13)).pack(side="left", padx=5)

    def _download_and_install_update(self):
        """Télécharge et installe la mise à jour"""
        self.log("=" * 60)
        self.log("🔄 TÉLÉCHARGEMENT DE LA MISE À JOUR")
        self.log("=" * 60)
        self.log("▶ Téléchargement en cours depuis kpi-tech.ca...")

        # Créer une popup de progression
        progress_dialog = tk.Toplevel(self)
        progress_dialog.title("Téléchargement en cours...")
        progress_dialog.geometry("450x200")
        progress_dialog.resizable(False, False)
        progress_dialog.transient(self)
        progress_dialog.grab_set()

        # Centrer
        progress_dialog.update_idletasks()
        x = (progress_dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (progress_dialog.winfo_screenheight() // 2) - (200 // 2)
        progress_dialog.geometry(f"+{x}+{y}")

        # Icône
        try:
            base_path = get_base_path()
            icon_path = os.path.join(base_path, "mainicon.ico")
            if os.path.exists(icon_path):
                progress_dialog.iconbitmap(icon_path)
        except:
            pass

        frame = ctk.CTkFrame(progress_dialog, fg_color="#1e1e1e")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        status_label = ctk.CTkLabel(frame,
                                    text="Téléchargement en cours...",
                                    font=ctk.CTkFont(size=14, weight="bold"))
        status_label.pack(pady=10)

        progress_bar = ctk.CTkProgressBar(frame, width=380)
        progress_bar.pack(pady=10)
        progress_bar.set(0)

        size_label = ctk.CTkLabel(frame,
                                  text="0 MB / 0 MB",
                                  font=ctk.CTkFont(size=11),
                                  text_color="#9ca3af")
        size_label.pack(pady=5)

        def update_progress(downloaded, total):
            """Mise à jour de la barre de progression"""
            if total > 0:
                percent = min(downloaded / total, 1.0)
                progress_bar.set(percent)

                dl_mb = downloaded / (1024 * 1024)
                total_mb = total / (1024 * 1024)
                size_label.configure(text=f"{dl_mb:.1f} MB / {total_mb:.1f} MB")
                self.log(f"  Téléchargé: {dl_mb:.1f} MB / {total_mb:.1f} MB ({percent*100:.0f}%)")

        def worker():
            try:
                # Téléchargement
                update_file = download_update(update_progress)

                if not update_file:
                    self.after(0, lambda: progress_dialog.destroy())
                    self.after(0, lambda: self.log("❌ Échec du téléchargement"))
                    self.after(0, lambda: messagebox.showerror(
                        "Erreur",
                        "Le téléchargement a échoué.\nVeuillez réessayer."))
                    return

                self.after(0, lambda: status_label.configure(
                    text="✅ Téléchargement terminé !"))
                self.after(0, lambda: self.log("✅ Téléchargement terminé"))

                time.sleep(1)

                # Installation
                self.after(0, lambda: status_label.configure(
                    text="Installation en cours..."))
                self.after(0, lambda: self.log("▶ Lancement de l'installation..."))

                time.sleep(1)

                if install_update(update_file):
                    self.after(0, lambda: self.log("✅ Mise à jour lancée"))
                    self.after(0, lambda: self.log("⚠️  L'application va redémarrer..."))
                    self.after(0, lambda: progress_dialog.destroy())

                    # Fermer IMMÉDIATEMENT l'application
                    import sys
                    time.sleep(0.5)
                    sys.exit(0)
                else:
                    self.after(0, lambda: progress_dialog.destroy())
                    self.after(0, lambda: self.log("❌ Échec de l'installation"))
                    self.after(0, lambda: messagebox.showerror(
                        "Erreur",
                        "L'installation a échoué.\nVeuillez installer manuellement."))

            except Exception as e:
                self.after(0, lambda: progress_dialog.destroy())
                self.after(0, lambda: self.log(f"❌ Erreur: {e}"))
                self.after(0, lambda: messagebox.showerror("Erreur", str(e)))

        threading.Thread(target=worker, daemon=True).start()
