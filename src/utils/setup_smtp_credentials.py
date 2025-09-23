#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup SMTP Credentials

Dieses Skript hilft bei der Einrichtung der verschlüsselten SMTP-Credentials.
"""

import os
import sys
import getpass
import logging
import os.path

# Füge das Hauptverzeichnis zum Pfad hinzu, damit wir die Module importieren können
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils.credential_manager import CredentialManager

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SetupSMTPCredentials")

def main():
    """Hauptfunktion"""
    print("=== SMTP-Credentials Einrichtung ===")
    print("Dieses Skript speichert deine SMTP-Anmeldedaten verschlüsselt.")
    print("Die Daten werden für den E-Mail-Versand von Benachrichtigungen verwendet.")
    print()
    
    # Credentials Manager initialisieren
    try:
        cred_manager = CredentialManager()
    except Exception as e:
        logger.error(f"Fehler beim Initialisieren des Credential Managers: {e}")
        print(f"Fehler: {e}")
        return 1
    
    # Benutzername abfragen
    smtp_username = input("SMTP-Benutzername (E-Mail-Adresse): ")
    if not smtp_username:
        print("Fehler: Benutzername darf nicht leer sein.")
        return 1
    
    # Passwort abfragen (ohne Anzeige)
    smtp_password = getpass.getpass("SMTP-Passwort (wird nicht angezeigt): ")
    if not smtp_password:
        print("Fehler: Passwort darf nicht leer sein.")
        return 1
    
    # Passwort bestätigen
    confirm_password = getpass.getpass("Passwort bestätigen: ")
    if smtp_password != confirm_password:
        print("Fehler: Passwörter stimmen nicht überein.")
        return 1
    
    # Credentials speichern
    try:
        # Stelle sicher, dass das config-Verzeichnis existiert
        os.makedirs("config", exist_ok=True)
        
        # Speichere die Credentials im config-Verzeichnis
        cred_manager.save_credentials(smtp_username, smtp_password, "config/smtp_credentials.enc")
        print("\nSMTP-Credentials wurden erfolgreich verschlüsselt und gespeichert.")
        print("Datei: config/smtp_credentials.enc")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Credentials: {e}")
        print(f"Fehler beim Speichern der Credentials: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
