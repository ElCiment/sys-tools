"""
Service de gestion réseau
Gère les opérations réseau: vérification de ports, récupération de mots de passe WiFi, etc.
"""
import socket
import subprocess
import re
import unicodedata
import threading
from utils.system_utils import is_admin, relaunch_as_admin


def check_tcp_port(host, port, log_fn):
    """
    Vérifie si un port TCP est accessible depuis l'EXTÉRIEUR (internet)
    Utilise plusieurs services de vérification de port pour plus de fiabilité
    
    Args:
        host (str): Adresse de l'hôte (ignoré, utilise l'IP publique)
        port (int): Numéro de port
        log_fn (callable): Fonction de logging
    """
    log_fn(f"🔎 Vérification de l'accessibilité EXTERNE du port {port}...")
    log_fn("⏳ Test depuis l'extérieur (internet)...")
    
    try:
        import urllib.request
        import urllib.parse
        import json
        
        # Récupérer l'IP publique d'abord
        log_fn("📡 Récupération de votre IP publique...")
        try:
            ip_response = urllib.request.urlopen('https://api.ipify.org?format=json', timeout=5)
            public_ip = json.loads(ip_response.read().decode())['ip']
        except:
            # Backup API
            ip_response = urllib.request.urlopen('https://api.my-ip.io/ip', timeout=5)
            public_ip = ip_response.read().decode().strip()
        
        log_fn(f"🌐 Votre IP publique: {public_ip}")
        
        # Vérifier le port avec API externe (seule méthode fiable)
        log_fn(f"🔍 Test du port {port} depuis l'extérieur...")
        
        is_open = None
        error_msg = ""
        
        # Méthode 1: API portchecker.co
        try:
            log_fn("  → Test via portchecker.co...")
            check_url = f'https://api.portchecker.co/check?host={public_ip}&port={port}'
            req = urllib.request.Request(check_url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json'
            })
            response = urllib.request.urlopen(req, timeout=20)
            result = json.loads(response.read().decode('utf-8'))
            is_open = result.get('open', False) or result.get('status', '').lower() == 'open'
            log_fn(f"  ✓ Réponse API: {result}")
        except Exception as e:
            log_fn(f"  ✗ Erreur API portchecker.co: {e}")
            error_msg = str(e)
            
        # Méthode 2 (backup): API yougetsignal.com
        if is_open is None:
            try:
                log_fn("  → Test via yougetsignal.com...")
                check_url = f'https://ports.yougetsignal.com/check-port.php'
                data = urllib.parse.urlencode({'remoteAddress': public_ip, 'portNumber': port}).encode()
                req = urllib.request.Request(check_url, data=data, headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Content-Type': 'application/x-www-form-urlencoded'
                })
                response = urllib.request.urlopen(req, timeout=20)
                text = response.read().decode('utf-8').lower()
                if 'open' in text:
                    is_open = True
                    log_fn(f"  ✓ Port détecté ouvert")
                elif 'closed' in text:
                    is_open = False
                    log_fn(f"  ✓ Port détecté fermé")
            except Exception as e:
                log_fn(f"  ✗ Erreur API yougetsignal: {e}")
                if not error_msg:
                    error_msg = str(e)
        
        # Afficher le résultat final
        log_fn("")
        if is_open is True:
            log_fn(f"✅ Port {port} est OUVERT et accessible depuis l'extérieur (internet)")
            log_fn(f"   Vous pouvez vous connecter via {public_ip}:{port}")
        elif is_open is False:
            log_fn(f"❌ Port {port} est FERMÉ ou inaccessible depuis l'extérieur")
            log_fn(f"   Le port n'est pas ouvert dans votre routeur/firewall")
            log_fn(f"   Pour l'ouvrir: configurez le NAT/Port Forwarding dans votre routeur")
        else:
            log_fn(f"⚠️  Impossible de vérifier le port {port}")
            log_fn(f"   Erreur: {error_msg}")
            log_fn(f"   Vérifiez manuellement sur: https://canyouseeme.org")
        
    except Exception as e:
        log_fn(f"❌ Erreur générale: {e}")
        log_fn(f"⚠️  Vérifiez manuellement le port sur: https://canyouseeme.org")


def _decode_bytes(b):
    """
    Tente de décoder des bytes avec différents encodages
    
    Args:
        b (bytes): Données à décoder
    
    Returns:
        str: Chaîne décodée
    """
    for enc in ("cp1252", "cp850", "utf-8", "latin-1"):
        try:
            return b.decode(enc)
        except Exception:
            continue
    return b.decode("utf-8", errors="replace")


def _normalize_text(s):
    """
    Normalise le texte pour gérer les encodages corrompus de Windows
    
    Args:
        s (str): Texte à normaliser
    
    Returns:
        str: Texte normalisé
    """
    s = unicodedata.normalize("NFKC", s)
    
    replacements = {
        "Ã©": "é", "Ã¨": "è", "Ãª": "ê", "Ã«": "ë", "Ã ": "à",
        "Ã¢": "â", "Ã´": "ô", "Ã¹": "ù", "Ã»": "û", "Ã§": "ç",
        "Â": "", "\u00A0": " "
    }
    
    for k, v in replacements.items():
        s = s.replace(k, v)
    
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s)
    return s


def get_wifi_passwords(log_fn):
    """
    Récupère les mots de passe WiFi sauvegardés
    
    Args:
        log_fn (callable): Fonction de logging
    """
    if not is_admin():
        log_fn("🔼 Nécessite les droits administrateur pour récupérer les mots de passe WiFi")
        try:
            relaunch_as_admin()
        except Exception as e:
            log_fn(f"❌ Impossible de relancer en admin: {e}")
        return
    
    log_fn("▶ Récupération des profils WiFi et mots de passe...")
    
    try:
        proc = subprocess.run(
            ["netsh", "wlan", "show", "profiles"],
            capture_output=True, text=False, check=True
        )
        stdout = _normalize_text(_decode_bytes(proc.stdout))
        
        profiles = []
        for line in stdout.splitlines():
            m = re.search(
                r'(?:Profil\s+Tous\s+les\s+utilisateurs|All User Profile|Profil|Profile)[^:]*:\s*(.+)$',
                line.strip(), flags=re.IGNORECASE
            )
            if m:
                name = m.group(1).strip().strip('"')
                if name:
                    profiles.append(name)
        
        profiles = list(dict.fromkeys(profiles))
        
        if not profiles:
            log_fn("❌ Aucun profil WiFi trouvé")
            return
        
        log_fn("----- Profils WiFi trouvés -----")
        for p in profiles:
            log_fn(f"📶 Profil: {p}")
        
        log_fn("----- Mots de passe -----")
        for profile in profiles:
            try:
                password_proc = subprocess.run(
                    ["netsh", "wlan", "show", "profile", "name=" + profile, "key=clear"],
                    capture_output=True, text=False, check=True
                )
                out = _normalize_text(_decode_bytes(password_proc.stdout))
                
                m_pwd = re.search(
                    r'(?im)(?:contenu\s*(?:de\s*la\s*)?cle|cont.*de.*la.*cle|key\s*content|contenu\s*de\s*la\s*cl[eé])[^\:]*:\s*([^\r\n]+)',
                    out
                )
                
                pwd = m_pwd.group(1).strip() if m_pwd else "Non trouvé"
                log_fn(f"🔑 {profile}: {pwd}")
                
            except subprocess.CalledProcessError as e:
                log_fn(f"❌ Erreur pour {profile}: Impossible de récupérer le mot de passe")
            except Exception as e:
                log_fn(f"❌ Erreur inattendue pour {profile}: {e}")
        
        log_fn("✅ Récupération terminée")
        
    except Exception as e:
        log_fn(f"❌ Erreur globale: {e}")


def get_teamviewer_id():
    """
    Récupère l'ID TeamViewer
    
    Returns:
        str: ID TeamViewer ou message d'erreur
    """
    try:
        res = subprocess.check_output(
            r'reg query "HKLM\SOFTWARE\WOW6432Node\TeamViewer" /v ClientID',
            shell=True, text=True, stderr=subprocess.DEVNULL
        )
        tv_id_raw = res.strip().split()[-1]
        return str(int(tv_id_raw, 16)) if tv_id_raw.startswith("0x") else tv_id_raw
    except Exception:
        try:
            res = subprocess.check_output(
                r'reg query "HKLM\SOFTWARE\TeamViewer" /v ClientID',
                shell=True, text=True, stderr=subprocess.DEVNULL
            )
            tv_id_raw = res.strip().split()[-1]
            return str(int(tv_id_raw, 16)) if tv_id_raw.startswith("0x") else tv_id_raw
        except Exception:
            return "Non installé ou introuvable"


def get_anydesk_id():
    """
    Récupère l'ID AnyDesk
    
    Returns:
        str: ID AnyDesk ou message d'erreur
    """
    try:
        res = subprocess.check_output(
            r'reg query "HKLM\SOFTWARE\AnyDesk" /v "ClientID"',
            shell=True, text=True, stderr=subprocess.DEVNULL
        )
        return res.strip().split()[-1]
    except Exception:
        try:
            res = subprocess.check_output(
                r'reg query "HKLM\SOFTWARE\WOW6432Node\AnyDesk" /v "ClientID"',
                shell=True, text=True, stderr=subprocess.DEVNULL
            )
            return res.strip().split()[-1]
        except Exception:
            return "Non installé ou introuvable"


def show_wifi_passwords(log_fn):
    """
    Affiche tous les mots de passe WiFi enregistrés dans la console
    
    Args:
        log_fn (callable): Fonction de logging
    """
    if not is_admin():
        log_fn("🔼 Nécessite les droits administrateur")
        try:
            relaunch_as_admin()
        except Exception as e:
            log_fn(f"❌ Impossible de relancer en admin: {e}")
        return
    
    def worker():
        try:
            log_fn("▶ Récupération des profils WiFi...")
            
            # Lister tous les profils
            profiles_result = subprocess.run(
                ["netsh", "wlan", "show", "profiles"],
                capture_output=True, text=True, encoding="utf-8", errors="ignore"
            )
            
            if profiles_result.returncode != 0:
                log_fn("❌ Impossible de lister les profils WiFi")
                return
            
            # Extraire les noms des profils
            profiles = []
            for line in profiles_result.stdout.splitlines():
                if "Profil Tous les utilisateurs" in line or "All User Profile" in line:
                    # Format: "    Profil Tous les utilisateurs : NomDuReseau"
                    parts = line.split(":")
                    if len(parts) >= 2:
                        profile_name = parts[1].strip()
                        profiles.append(profile_name)
            
            if not profiles:
                log_fn("⚠️ Aucun profil WiFi trouvé")
                return
            
            log_fn(f"✅ {len(profiles)} profil(s) WiFi trouvé(s)")
            log_fn("=" * 60)
            
            # Pour chaque profil, afficher le mot de passe
            for profile in profiles:
                try:
                    password_result = subprocess.run(
                        ["netsh", "wlan", "show", "profile", profile, "key=clear"],
                        capture_output=True, text=True, encoding="utf-8", errors="ignore"
                    )
                    
                    password = "Non disponible"
                    for line in password_result.stdout.splitlines():
                        if "Contenu de la clé" in line or "Key Content" in line:
                            parts = line.split(":")
                            if len(parts) >= 2:
                                password = parts[1].strip()
                                break
                    
                    log_fn(f"📶 {profile}")
                    log_fn(f"   🔑 Mot de passe: {password}")
                    log_fn("")
                    
                except Exception as e:
                    log_fn(f"❌ Erreur pour {profile}: {e}")
            
            log_fn("=" * 60)
            log_fn("✅ Récupération terminée")
            
        except Exception as e:
            log_fn(f"❌ Erreur générale: {e}")
    
    threading.Thread(target=worker, daemon=True).start()
