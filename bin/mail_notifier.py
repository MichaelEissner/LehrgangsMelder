#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mail Notifier

Dieses Programm überwacht die termine.json Datei auf neue Einträge
und sendet E-Mail-Benachrichtigungen für neue Lehrgänge.
"""

import os
import json
import logging
import smtplib
import datetime
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from dotenv import load_dotenv
import sys
import os

# Füge das Hauptverzeichnis zum Pfad hinzu, damit wir die Module importieren können
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils.credential_manager import CredentialManager

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/mail_notifier.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MailNotifier")

# Konstanten
JSON_FILE = "data/termine.json"
LAST_SENT_FILE = "data/last_sent.json"
EMAIL_ARCHIVE_DIR = "data/email_archive"

def lade_json(datei):
    """Lädt JSON oder gibt leere Liste zurück"""
    if not os.path.exists(datei):
        return []
    try:
        with open(datei, "r", encoding="utf-8") as f:
            daten = json.load(f)
        if not isinstance(daten, list):
            return []
        return daten
    except json.JSONDecodeError:
        return []

def speichere_json(datei, daten):
    """Speichert Daten als JSON"""
    with open(datei, "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, indent=4)

def erstelle_key(eintrag):
    """Erstellt einen eindeutigen Schlüssel für einen Eintrag"""
    termin = eintrag['termin']
    beschreibung = eintrag['beschreibung']
    
    # Extrahiere den Kursnamen aus der Beschreibung
    kursname = beschreibung
    if " - " in beschreibung:
        kursname = beschreibung.split(" - ")[0]
    
    # Wir verwenden den Termin und den Kursnamen (ohne Status) für den Key
    # So werden auch mehrere Lehrgänge desselben Typs mit unterschiedlichen Terminen erkannt,
    # unabhängig vom Status (geplant, eingeladen, etc.)
    return f"{termin}|{kursname}"

def formatiere_eintrag_html(eintrag):
    """Formatiert einen Eintrag als HTML für die E-Mail"""
    # Extrahiere Status aus der Beschreibung (z.B. "Atemschutzgeräteträger - eingeladen")
    beschreibung = eintrag["beschreibung"]
    status = "unbekannt"
    
    if " - " in beschreibung:
        teile = beschreibung.split(" - ")
        kurs = teile[0]
        status = teile[1]
    else:
        kurs = beschreibung
    
    # Formatiere den Ort schöner (mit Zeilenumbrüchen)
    ort = eintrag["ort"].replace(". ", ".<br>")
    
    # Erstelle HTML-Tabelle für den Eintrag
    html = f"""
    <div style="margin-bottom: 20px; border: 1px solid #ddd; padding: 15px; border-radius: 5px;">
        <h2 style="color: #d9534f; margin-top: 0;">{kurs}</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd; width: 120px;"><strong>Termin:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{eintrag["termin"]}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Status:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{status}</td>
            </tr>
            <tr>
                <td style="padding: 8px; vertical-align: top;"><strong>Ort:</strong></td>
                <td style="padding: 8px;">{ort}</td>
            </tr>
        </table>
    </div>
    """
    return html

def formatiere_eintrag_text(eintrag):
    """Formatiert einen Eintrag als Text für die E-Mail"""
    # Extrahiere Status aus der Beschreibung
    beschreibung = eintrag["beschreibung"]
    status = "unbekannt"
    
    if " - " in beschreibung:
        teile = beschreibung.split(" - ")
        kurs = teile[0]
        status = teile[1]
    else:
        kurs = beschreibung
    
    text = f"""
{kurs}
-----------------------------------------
Termin: {eintrag["termin"]}
Status: {status}
Ort: {eintrag["ort"]}
-----------------------------------------
"""
    return text

def speichere_email_als_datei(betreff, text_content, html_content=None):
    """Speichert eine E-Mail als Textdatei im Archiv-Verzeichnis"""
    # Prüfen, ob E-Mails gespeichert werden sollen
    save_emails = os.getenv("SAVE_EMAILS", "True").lower() == "true"
    if not save_emails:
        return
    
    # Prüfen, ob leere E-Mails gespeichert werden sollen
    save_empty_emails = os.getenv("SAVE_EMPTY_EMAILS", "True").lower() == "true"
    if not save_empty_emails and "Keine neuen Lehrgänge gefunden" in betreff:
        return
    
    # Verzeichnis für E-Mail-Archiv erstellen, falls es nicht existiert
    email_dir = os.getenv("EMAIL_ARCHIVE_DIR", EMAIL_ARCHIVE_DIR)
    os.makedirs(email_dir, exist_ok=True)
    
    # Zeitstempel für den Dateinamen erstellen
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Betreff für den Dateinamen bereinigen (ungültige Zeichen entfernen)
    safe_betreff = re.sub(r'[\\/*?:"<>|]', "", betreff)
    safe_betreff = safe_betreff.replace(" ", "_")
    
    # Dateiname erstellen
    filename = f"{email_dir}/{timestamp}_{safe_betreff}.txt"
    
    # E-Mail-Inhalt in Datei speichern
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Betreff: {betreff}\n")
            f.write(f"Datum: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write("-" * 50 + "\n\n")
            f.write(text_content)
        
        logger.info(f"E-Mail als Datei gespeichert: {filename}")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der E-Mail als Datei: {e}")

def sende_email(neue_eintraege):
    """Sendet eine E-Mail mit den neuen Einträgen
    
    Args:
        neue_eintraege (list): Liste der neuen Einträge
        
    Returns:
        bool: True, wenn die E-Mail erfolgreich gesendet wurde, sonst False
    
    Hinweis: Diese Funktion sendet nur E-Mails, wenn neue Einträge vorhanden sind.
    """
    # Wenn keine neuen Einträge vorhanden sind, keine E-Mail senden
    if not neue_eintraege:
        logger.info("Keine neuen Einträge zum Senden vorhanden")
        return False
    try:
        # E-Mail-Konfiguration aus Umgebungsvariablen laden
        smtp_server = os.getenv("SMTP_SERVER", "smtp.strato.de")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL", "")
        recipient_emails_str = os.getenv("RECIPIENT_EMAIL", "")
        
        # Empfänger-E-Mails aufteilen (kommagetrennt)
        recipient_emails = [email.strip() for email in recipient_emails_str.split(",") if email.strip()]
        if not recipient_emails:
            logger.error("Keine Empfänger-E-Mail-Adressen konfiguriert")
            return False
        
        # Credentials laden
        cred_manager = CredentialManager()
        
        # Versuche zuerst, SMTP-Credentials aus Umgebungsvariablen zu laden
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        # Wenn keine Umgebungsvariablen vorhanden sind, verwende verschlüsselte Credentials
        if not smtp_username or not smtp_password:
            try:
                smtp_username, smtp_password = cred_manager.load_credentials("config/smtp_credentials.enc")
                logger.info("SMTP-Anmeldedaten aus verschlüsselter Datei geladen")
            except Exception as e:
                logger.error(f"Fehler beim Laden der SMTP-Credentials: {e}")
                # Wenn keine SMTP-Credentials gefunden wurden, aber E-Mail-Archivierung aktiviert ist,
                # speichern wir die E-Mail trotzdem als Datei
                return False
        else:
            logger.info("SMTP-Anmeldedaten aus Umgebungsvariablen geladen")
        
        # Betreff erstellen
        betreff = f"Neue Lehrgänge gefunden ({len(neue_eintraege)})"
        
        # Text-Version der E-Mail
        text_content = f"Neue Lehrgänge gefunden: {len(neue_eintraege)}\n\n"
        for eintrag in neue_eintraege:
            text_content += formatiere_eintrag_text(eintrag)
        
        # HTML-Version der E-Mail
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                h1 {{ color: #d9534f; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #777; border-top: 1px solid #ddd; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Neue Lehrgänge gefunden: {len(neue_eintraege)}</h1>
                <p>Folgende neue Lehrgänge wurden gefunden:</p>
                
                {"".join(formatiere_eintrag_html(eintrag) for eintrag in neue_eintraege)}
                
                <div class="footer">
                    <p>Diese E-Mail wurde automatisch generiert am {datetime.datetime.now().strftime("%d.%m.%Y um %H:%M")} Uhr.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # E-Mail als Datei speichern
        speichere_email_als_datei(betreff, text_content, html_content)
        
        
        # E-Mail erstellen
        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        msg["To"] = ", ".join(recipient_emails)
        msg["Subject"] = betreff
        
        # Beide Versionen zur E-Mail hinzufügen
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        # E-Mail senden
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        logger.info(f"E-Mail-Benachrichtigung für {len(neue_eintraege) if neue_eintraege else 'keine'} neue Einträge gesendet an: {', '.join(recipient_emails)}")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Senden der E-Mail: {e}")
        return False

def main():
    """Hauptfunktion"""
    # Umgebungsvariablen laden
    load_dotenv("config/.env")
    
    # Aktuelle Einträge laden
    aktuelle_eintraege = lade_json(JSON_FILE)
    logger.info(f"{len(aktuelle_eintraege)} Einträge aus {JSON_FILE} geladen")
    
    # Zuletzt gesendete Einträge laden
    letzte_eintraege = lade_json(LAST_SENT_FILE)
    logger.info(f"{len(letzte_eintraege)} Einträge aus {LAST_SENT_FILE} geladen")
    
    # Schlüssel der letzten Einträge erstellen
    letzte_keys = {erstelle_key(eintrag) for eintrag in letzte_eintraege}
    
    # Neue Einträge finden
    neue_eintraege = []
    for eintrag in aktuelle_eintraege:
        key = erstelle_key(eintrag)
        if key not in letzte_keys:
            neue_eintraege.append(eintrag)
    
    logger.info(f"{len(neue_eintraege)} neue Einträge gefunden")
    
    # Betreff und Inhalt für E-Mail erstellen
    if neue_eintraege:
        betreff = f"Neue Lehrgänge gefunden ({len(neue_eintraege)})"
        text_content = f"Neue Lehrgänge gefunden: {len(neue_eintraege)}\n\n"
        for eintrag in neue_eintraege:
            text_content += formatiere_eintrag_text(eintrag)
    else:
        betreff = "Keine neuen Lehrgänge gefunden"
        text_content = "Es wurden keine neuen Lehrgänge gefunden.\n"
    
    # E-Mail als Datei speichern (auch wenn keine E-Mail gesendet wird)
    speichere_email_als_datei(betreff, text_content, None)
    
    
    # E-Mail nur senden, wenn neue Einträge gefunden wurden
    email_sent = False
    if neue_eintraege:
        try:
            email_sent = sende_email(neue_eintraege)
        except Exception as e:
            logger.error(f"Fehler beim Senden der E-Mail: {e}")
    else:
        logger.info("Keine neuen Einträge gefunden, keine E-Mail gesendet")
    
    # Die aktuellen Einträge als "gesendet" speichern, auch wenn der E-Mail-Versand fehlschlägt
    if neue_eintraege:
        speichere_json(LAST_SENT_FILE, aktuelle_eintraege)
        logger.info(f"Aktuelle Einträge in {LAST_SENT_FILE} gespeichert")

if __name__ == "__main__":
    main()

# Made with Bob
