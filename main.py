#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Outils - Système
Application de gestion système Windows avec interface graphique moderne
Point d'entrée principal de l'application
"""
import sys
import traceback
import os

try:
    import customtkinter as ctk
    from tkinter import messagebox
    from utils.system_utils import is_admin, relaunch_as_admin
    from ui.password_dialog import PasswordDialog
    from ui.main_window import ToolsApp
except Exception as e:
    error_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash_log.txt")
    with open(error_log, "w", encoding="utf-8") as f:
        f.write(f"Erreur au chargement:\n{traceback.format_exc()}")
    sys.exit(1)


def main():
    """Point d'entrée principal de l'application"""
    PASSWORDS = ["Log1tech", "Axios1694"]
    skip_password = "--skip-password" in sys.argv
    
    if not skip_password:
        # Fenêtre temporaire pour le dialogue de mot de passe
        root = ctk.CTk()
        root.withdraw()
        
        # Boucle d'authentification
        while True:
            entered_password = PasswordDialog.ask_password(root, "Authentification", PASSWORDS)
            
            # Annulation
            if entered_password is None:
                if messagebox.askyesno("Quitter", "Voulez-vous quitter l'application ?"):
                    root.destroy()
                    sys.exit(1)
                else:
                    continue
            
            # Mot de passe correct
            if entered_password in PASSWORDS:
                break
            else:
                # Mot de passe incorrect
                msg = ctk.CTkToplevel(root)
                msg.title("Erreur")
                msg.geometry("300x120")
                msg.resizable(False, False)
                ctk.CTkLabel(
                    msg, 
                    text="❌ Mot de passe incorrect", 
                    text_color="red", 
                    font=ctk.CTkFont(size=14)
                ).pack(pady=30)
                ctk.CTkButton(msg, text="OK", command=msg.destroy).pack()
                msg.grab_set()
                root.wait_window(msg)
        
        # Élévation des privilèges si nécessaire
        if not is_admin():
            try:
                relaunch_as_admin()
                root.destroy()
                sys.exit(0)
            except Exception as e:
                messagebox.showwarning(
                    "Mode normal",
                    f"Impossible de relancer en administrateur. L'application démarre en mode normal.\n\nErreur: {e}"
                )
        
        root.destroy()
    
    # Lancement de l'application principale
    try:
        app = ToolsApp()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Erreur au démarrage", f"L'application a rencontré une erreur:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        main()
    except Exception as e:
        error_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash_log.txt")
        with open(error_log, "w", encoding="utf-8") as f:
            f.write(f"Erreur fatale:\n{traceback.format_exc()}")
        sys.exit(1)
