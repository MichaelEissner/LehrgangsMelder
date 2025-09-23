#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run Monitor and Notify

Dieses Skript führt den Website-Monitor und den Mail-Notifier nacheinander aus,
um neue Lehrgänge zu finden und Benachrichtigungen zu senden.
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/run_monitor_and_notify.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RunMonitorAndNotify")

def run_command(command):
    """Führt einen Befehl aus und gibt das Ergebnis zurück"""
    logger.info(f"Führe Befehl aus: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"Befehl erfolgreich ausgeführt: {result.stdout.strip()}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Fehler beim Ausführen des Befehls: {e}")
        logger.error(f"Fehlerausgabe: {e.stderr}")
        return False, e.stderr

def main():
    """Hauptfunktion"""
    logger.info("Starte den Prozess zur Überwachung und Benachrichtigung")
    
    # Aktuelles Verzeichnis speichern
    current_dir = os.getcwd()
    logger.info(f"Aktuelles Verzeichnis: {current_dir}")
    
    # Datum und Uhrzeit für die Protokollierung
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Ausführung gestartet am: {now}")
    
    # 1. Monitor ausführen
    logger.info("1. Führe monitor.py aus...")
    success, output = run_command("python bin/monitor.py")
    if not success:
        logger.error("Fehler beim Ausführen von monitor.py")
        return 1
    
    # 2. Mail-Notifier ausführen
    logger.info("2. Führe mail_notifier.py aus...")
    success, output = run_command("python bin/mail_notifier.py")
    if not success:
        logger.error("Fehler beim Ausführen von mail_notifier.py")
        return 1
    
    # Erfolgsmeldung
    logger.info("Prozess erfolgreich abgeschlossen")
    return 0

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
