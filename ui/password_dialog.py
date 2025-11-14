"""
Dialogue de mot de passe
Interface de connexion sécurisée pour l'application
"""
import customtkinter as ctk
from PIL import Image, ImageTk
from utils.system_utils import get_base_path
import os


class PasswordDialog(ctk.CTkToplevel):
    """Dialogue d'authentification par mot de passe"""
    
    def __init__(self, parent, title="Authentification", correct_password="Log1tech"):
        super().__init__(parent)
        
        self.title(title)
        self.correct_password = correct_password
        self.result = None
      
        

        base_path = get_base_path()
        
        version_path = os.path.join(base_path, "version.txt")
        version_text = "Version inconnue"
        if os.path.exists(version_path):
            try:
                with open(version_path, "r", encoding="utf-8") as f:
                    version_text = f.read().strip()
            except Exception as e:
                print(f"Impossible de lire version.txt: {e}")
     
        
       
        # Définir l'icône
        icon_path = os.path.join(base_path, "mainicon.ico")
        try:
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Impossible de charger l'icône: {e}")
        
        # Logo
        logo_path = os.path.join(base_path, "mainlogo.png")
        if os.path.exists(logo_path):
            try:
                logo_image = Image.open(logo_path).resize((80, 80), Image.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                ctk.CTkLabel(self, image=self.logo_photo, text="").pack(pady=(10, 5))
            except Exception as e:
                print(f"Impossible de charger le logo: {e}")
        
        # Champ mot de passe
        ctk.CTkLabel(
            self, 
            text="Entrez le mot de passe :", 
            font=ctk.CTkFont(size=14)
        ).pack(pady=(5, 10))
        
        self.password_entry = ctk.CTkEntry(
            self, 
            show="*", 
            width=250, 
            font=ctk.CTkFont(size=14)
        )
        self.password_entry.pack(pady=(0, 0))
        self.password_entry.focus()
        
        self.error_label = ctk.CTkLabel(
            self, 
            text="", 
            text_color="#e05454", 
            font=ctk.CTkFont(size=12)
        )
        self.error_label.pack()
        
        # Frame pour les boutons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=(10, 2))  # 10 pixels au-dessus pour séparer du champ mot de passe
        ctk.CTkButton(button_frame, text="OK", width=100, command=self.on_ok).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Annuler", width=100, fg_color="#e05454",
                       hover_color="#c03a3a", command=self.on_cancel).pack(side="right", padx=10)

        # Label version juste en dessous
        ctk.CTkLabel(
            self,
            text=f"Version: {version_text}",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        ).pack(pady=(2, 5))  # 2 pixels au-dessus pour coller aux boutons, 5 en bas

        
        # Raccourcis clavier
        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.on_cancel())
        
        self.grab_set()
        self.after_idle(self.center_on_screen)
    
    def center_on_screen(self):
        """Centre la fenêtre sur l'écran"""
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (sw // 2) - (w // 2), (sh // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
    
    def on_ok(self):
        """Vérifie le mot de passe"""
        entered = self.password_entry.get()
        if entered == self.correct_password:
            self.result = entered
            self.destroy()
        else:
            self.error_label.configure(text="❌ Mot de passe incorrect.")
            self.password_entry.delete(0, "end")
            self.password_entry.focus()
    
    def on_cancel(self):
        """Annule l'authentification"""
        self.result = None
        self.destroy()
    
    @staticmethod
    def ask_password(parent, title="Authentification", correct_password="Log1tech"):
        """
        Affiche le dialogue et retourne le mot de passe saisi
        
        Args:
            parent: Fenêtre parente
            title (str): Titre du dialogue
            correct_password (str): Mot de passe attendu
        
        Returns:
            str or None: Mot de passe si correct, None si annulé
        """
        dialog = PasswordDialog(parent, title, correct_password)
        dialog.wait_window()
        return dialog.result
