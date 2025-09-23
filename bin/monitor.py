#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Monitor für Lehrgänge

Dieses Skript überwacht die Webseite des Kreisfeuerwehrverbands nach Lehrgängen
und speichert neue Einträge in einer JSON-Datei.
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
import logging
from dotenv import load_dotenv

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Monitor")

# Konstanten
URL = "https://www.kfv-esnt.de/index.asp?ID=1894&CAT=Ausbildung&SUBCAT=Termine%20Kreisausbildung&SPRACHE=1"
JSON_FILE = "data/termine.json"

def bereinige_text(text):
    """Tabs, mehrfach Leerzeichen und Zeilenumbrüche entfernen"""
    text = re.sub(r'\s+', ' ', text)  # Alle Whitespaces zu einem
    return text.strip()

def erstelle_key(termin, beschreibung):
    """Eindeutigen Key erzeugen, um Duplikate zu vermeiden"""
    # Bei Zeiträumen (Format: "10.10.2025 - 25.10.2025") den Zeitraum und den Kursnamen verwenden
    termin_clean = bereinige_text(termin).lower()
    
    # Extrahiere den Kursnamen aus der Beschreibung
    kursname = beschreibung
    if " - " in beschreibung:
        kursname = beschreibung.split(" - ")[0]
    
    kursname_clean = bereinige_text(kursname).lower()
    
    # Wir verwenden den Termin und den Kursnamen (ohne Status) für den Key
    # So werden auch mehrere Lehrgänge desselben Typs mit unterschiedlichen Terminen erkannt,
    # unabhängig vom Status (geplant, eingeladen, etc.)
    return f"{termin_clean}|{kursname_clean}"

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

def hole_suchbegriffe():
    """Holt die Suchbegriffe aus der Umgebungsvariablen"""
    search_text = os.getenv("SEARCH_TEXT", "")
    if not search_text:
        logger.warning("Keine Suchbegriffe konfiguriert, verwende Standardwerte")
        return ["TM2", "Atemschutz", "Truppmann"]
    
    # Suchbegriffe aufteilen und bereinigen
    suchbegriffe = [begriff.strip() for begriff in search_text.split(",") if begriff.strip()]
    logger.info(f"Suchbegriffe: {suchbegriffe}")
    return suchbegriffe

def extrahiere_termine_aus_tabelle(soup, suchbegriffe):
    """Extrahiert Termine aus der HTML-Tabelle"""
    gefundene_termine = []
    
    # Tabelle finden
    table = soup.find("table")
    if not table:
        logger.error("Keine Tabelle gefunden!")
        return []
    
    # Zeilen finden
    rows = table.find_all("tr")
    if len(rows) <= 1:
        logger.warning("Keine Datenzeilen in der Tabelle gefunden")
        return []
    
    # Erste Zeile überspringen (Überschriften)
    for row in rows[0:]:
        cols = row.find_all("td")
        if len(cols) != 3:
            continue
        
        # Termine extrahieren
        termin_text = cols[0].get_text(separator="\n")
        termine = [t.strip() for t in termin_text.split("\n") if t.strip()]
        if not termine:
            continue
            
        # Beschreibung extrahieren
        beschreibung_element = cols[1]
        titel_tag = beschreibung_element.find("h3")
        titel = titel_tag.get_text(strip=True) if titel_tag else ""
        
        beschreibung_text = beschreibung_element.get_text(separator="\n")
        text_lines = [line.strip() for line in beschreibung_text.split("\n") if line.strip()]
        status = text_lines[-1] if text_lines else ""
        
        beschreibung = f"{titel} - {status}" if titel else status
        
        # Ort extrahieren
        ort_text = cols[2].get_text(separator="\n")
        ort = bereinige_text(ort_text)
        
        # Prüfen, ob einer der Suchbegriffe im Titel oder in der Beschreibung vorkommt
        beschreibung_lower = beschreibung.lower()
        if not any(begriff.lower() in beschreibung_lower for begriff in suchbegriffe):
            continue
            
        # Extrahiere den Kursnamen und Status aus der Beschreibung
        kursname = beschreibung
        status = ""
        if " - " in beschreibung:
            teile = beschreibung.split(" - ")
            kursname = teile[0]
            status = teile[1]
            
        # Wenn mehrere Termine vorhanden sind, handelt es sich um einen Zeitraum
        if len(termine) >= 2:
            # Sortiere die Termine (falls sie nicht in chronologischer Reihenfolge sind)
            termine.sort()
            # Erstelle einen Zeitraum vom ersten bis zum letzten Termin
            termin_zeitraum = f"{termine[0]} - {termine[-1]}"
            gefundene_termine.append({
                "termin": termin_zeitraum,
                "beschreibung": beschreibung,
                "ort": ort,
                "kursname": kursname,
                "status": status
            })
        else:
            # Bei nur einem Termin, diesen direkt verwenden
            for termin in termine:
                gefundene_termine.append({
                    "termin": termin,
                    "beschreibung": beschreibung,
                    "ort": ort,
                    "kursname": kursname,
                    "status": status
                })
    
    return gefundene_termine

def main():
    """Hauptfunktion"""
    # Umgebungsvariablen laden
    load_dotenv("config/.env")
    
    # Suchbegriffe laden
    suchbegriffe = hole_suchbegriffe()
    
    # Webseite abrufen
    logger.info(f"Rufe Webseite ab: {URL}")
    try:
        response = requests.get(URL)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "lxml")
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Webseite: {e}")
        return

    # Termine extrahieren
    gefundene_termine = extrahiere_termine_aus_tabelle(soup, suchbegriffe)
    
    # Vorhandene Daten laden
    daten = lade_json(JSON_FILE)
    vorhandene_keys = set(erstelle_key(e["termin"], e["beschreibung"]) for e in daten)
    
    # Neue Einträge identifizieren
    neue_eintraege = []
    for termin in gefundene_termine:
        key = erstelle_key(termin["termin"], termin["beschreibung"])
        if key not in vorhandene_keys:
            neue_eintraege.append(termin)
            vorhandene_keys.add(key)

    # Neue Einträge speichern
    if neue_eintraege:
        daten.extend(neue_eintraege)
        speichere_json(JSON_FILE, daten)
        logger.info(f"{len(neue_eintraege)} neue Einträge gespeichert.")
    else:
        logger.info("Keine neuen Einträge gefunden.")
    
    # Statistik ausgeben
    logger.info(f"Insgesamt {len(gefundene_termine)} passende Einträge gefunden.")
    logger.info(f"Davon {len(neue_eintraege)} neue Einträge.")

if __name__ == "__main__":
    main()

# Made with Bob
