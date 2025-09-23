#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Credential Manager

Diese Klasse verwaltet die sicheren Credentials für die Anwendung.
"""

import os
import logging
from cryptography.fernet import Fernet

# Logger konfigurieren
logger = logging.getLogger("WebsiteMonitor.CredentialManager")

class CredentialManager:
    """Verwaltet die sicheren Credentials für die Anwendung."""
    
    def __init__(self, key_file="secret.key"):
        """Initialisiert den Credential Manager.
        
        Args:
            key_file (str): Pfad zur Datei mit dem Verschlüsselungsschlüssel
        """
        self.key_file = key_file
        self.key = self._load_or_generate_key()
        self.cipher_suite = Fernet(self.key)
        
    def _load_or_generate_key(self):
        """Lädt einen existierenden Schlüssel oder generiert einen neuen."""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, "rb") as key_file:
                    return key_file.read()
            else:
                key = Fernet.generate_key()
                with open(self.key_file, "wb") as key_file:
                    key_file.write(key)
                logger.info(f"Neuer Verschlüsselungsschlüssel in {self.key_file} generiert")
                return key
        except Exception as e:
            logger.error(f"Fehler beim Laden/Generieren des Schlüssels: {e}")
            raise
    
    def encrypt(self, data):
        """Verschlüsselt die übergebenen Daten.
        
        Args:
            data (str): Zu verschlüsselnde Daten
            
        Returns:
            bytes: Verschlüsselte Daten
        """
        if isinstance(data, str):
            data = data.encode()
        return self.cipher_suite.encrypt(data)
    
    def decrypt(self, encrypted_data):
        """Entschlüsselt die übergebenen Daten.
        
        Args:
            encrypted_data (bytes): Verschlüsselte Daten
            
        Returns:
            str: Entschlüsselte Daten
        """
        decrypted = self.cipher_suite.decrypt(encrypted_data)
        return decrypted.decode()
    
    def save_credentials(self, username, password, filename="credentials.enc"):
        """Speichert Benutzername und Passwort verschlüsselt in einer Datei.
        
        Args:
            username (str): Benutzername
            password (str): Passwort
            filename (str): Zieldatei für die verschlüsselten Credentials
        """
        credentials = f"{username}:{password}"
        encrypted = self.encrypt(credentials)
        
        with open(filename, "wb") as f:
            f.write(encrypted)
        logger.info(f"Verschlüsselte Credentials in {filename} gespeichert")
    
    def load_credentials(self, filename="credentials.enc"):
        """Lädt und entschlüsselt Credentials aus einer Datei.
        
        Args:
            filename (str): Datei mit den verschlüsselten Credentials
            
        Returns:
            tuple: (username, password)
        """
        try:
            with open(filename, "rb") as f:
                encrypted = f.read()
            
            decrypted = self.decrypt(encrypted)
            username, password = decrypted.split(":", 1)
            return username, password
        except Exception as e:
            logger.error(f"Fehler beim Laden der Credentials: {e}")
            raise

# Made with Bob
