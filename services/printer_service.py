"""
Service de gestion des imprimantes
Gère la communication TCP/IP et série avec les imprimantes ESC/P
"""
import socket
import time


def build_message(n_lines_each=20, text="Test Test Test Test Test Test Test Test",
                  mode="tcp", ip="", port="", com_port="", baud=""):
    """
    Construit un message ESC/P pour imprimantes thermiques
    
    Args:
        n_lines_each (int): Nombre de lignes par section (noir/rouge)
        text (str): Texte à imprimer
        mode (str): "tcp" ou "com"
        ip (str): Adresse IP pour TCP
        port (str): Port pour TCP
        com_port (str): Port COM pour série
        baud (str): Baudrate pour série
    
    Returns:
        bytes: Message formaté ESC/P
    """
    ESC = b'\x1b'
    black_cmd = ESC + b'r' + bytes([0])
    red_cmd = ESC + b'r' + bytes([1])
    cut_thermal = ESC + b'i'
    crlf = b'\r\n'

    msg = bytearray()
    
    # Header info
    msg += black_cmd
    msg += b"***************************************" + crlf
    msg += b"TEST D'IMPRESSION - INFO CONNEXION" + crlf
    msg += b"***************************************" + crlf
    
    if mode.lower() == "tcp":
        msg += black_cmd + f"Mode: TCP/IP".encode() + crlf
        msg += black_cmd + f"IP: {ip}".encode() + crlf
        msg += black_cmd + f"Port: {port}".encode() + crlf
    else:
        msg += black_cmd + f"Mode: COM".encode() + crlf
        msg += black_cmd + f"Port COM: {com_port}".encode() + crlf
        msg += black_cmd + f"Baudrate: {baud}".encode() + crlf
    msg += crlf

    # Section Noir
    msg += black_cmd
    msg += b"***************************************" + crlf
    msg += b"TEST D'IMPRESSION - SECTION NOIR:" + crlf
    msg += b"***************************************" + crlf
    for _ in range(n_lines_each):
        msg += black_cmd + text.encode() + crlf
    msg += crlf

    # Section Rouge
    msg += red_cmd
    msg += b"***************************************" + crlf
    msg += b"TEST D'IMPRESSION - SECTION ROUGE:" + crlf
    msg += b"***************************************" + crlf
    for _ in range(n_lines_each):
        msg += red_cmd + text.encode() + crlf
    msg += crlf

    # Fin
    msg += black_cmd + b"Le Papier Devrait Couper ici" + crlf
    msg += b'\r\n' * 8
    msg += cut_thermal + crlf
    
    return bytes(msg)


def send_tcp(ip, port, data, log_fn):
    """
    Envoie des données via TCP à une imprimante
    
    Args:
        ip (str): Adresse IP
        port (int): Port TCP
        data (bytes): Données à envoyer
        log_fn (callable): Fonction de logging
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    
    try:
        s.connect((ip, port))
        s.sendall(data)
        log_fn(f"✅ Envoi TCP réussi vers {ip}:{port}")
    except Exception as e:
        log_fn(f"❌ Erreur TCP: {e}")
    finally:
        try:
            s.close()
        except:
            pass


def send_serial(port, baudrate, data, log_fn):
    """
    Envoie des données via port série à une imprimante
    
    Args:
        port (str): Port COM
        baudrate (int): Vitesse de communication
        data (bytes): Données à envoyer
        log_fn (callable): Fonction de logging
    """
    try:
        import serial
        with serial.Serial(port, baudrate, timeout=1) as ser:
            ser.write(data)
            ser.flush()
        log_fn(f"✅ Envoi série réussi vers {port} @ {baudrate}")
    except Exception as e:
        log_fn(f"❌ Erreur série: {e}")


def get_serial_ports():
    """
    Liste les ports série disponibles
    
    Returns:
        list: Liste des ports COM disponibles
    """
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [p.device for p in ports]
    except Exception:
        return []
