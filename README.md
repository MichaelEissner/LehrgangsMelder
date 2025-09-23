# Lehrgangs-Monitor mit E-Mail-Benachrichtigung

Dieses System überwacht die Webseite des Kreisfeuerwehrverbands nach bestimmten Lehrgängen und sendet automatisch E-Mail-Benachrichtigungen, wenn neue passende Lehrgänge gefunden werden.

## Funktionsweise

1. **Datenerfassung**: Das Skript `monitor.py` ruft die Webseite des Kreisfeuerwehrverbands ab und extrahiert Lehrgangsdaten aus der HTML-Tabelle.
2. **Filterung**: Es werden nur Lehrgänge berücksichtigt, die den konfigurierten Suchbegriffen entsprechen.
3. **Zeitraumerkennung**: Mehrere Termine für denselben Lehrgang werden als Zeitraum erkannt (z.B. "10.10.2025 - 25.10.2025").
4. **Datenspeicherung**: Die gefundenen Lehrgänge werden in der Datei `termine.json` gespeichert.
5. **Erkennung neuer Einträge**: Das Skript `mail_notifier.py` vergleicht die aktuellen Einträge mit den zuletzt gesendeten.
6. **Benachrichtigung**: E-Mail-Benachrichtigungen werden an einen oder mehrere Empfänger gesendet, aber nur wenn neue Lehrgänge gefunden wurden.
7. **E-Mail-Archivierung**: Alle gesendeten E-Mails werden als Textdateien gespeichert.
8. **Statusverfolgung**: Nach erfolgreichem Versand werden die aktuellen Einträge in `last_sent.json` gespeichert.

## Installation

1. Stelle sicher, dass Python 3.6 oder höher installiert ist.
2. Installiere die erforderlichen Pakete:
   ```
   pip install requests beautifulsoup4 python-dotenv cryptography
   ```
3. Kopiere die `.env.example` Datei zu `.env` und passe die Einstellungen an:
   ```
   cp config/.env.example config/.env
   ```
4. Bearbeite die `.env` Datei und füge deine SMTP-Anmeldedaten und Suchbegriffe hinzu.

## Konfiguration

### Suchbegriffe (Filter)

In der `.env` Datei kannst du die Suchbegriffe für Lehrgänge festlegen:

```
# Mehrere Suchtexte können durch Kommas getrennt werden
SEARCH_TEXT=TM2,Atemschutz,Truppmann
```

Das System wird nur Lehrgänge berücksichtigen, die einen dieser Begriffe im Titel oder in der Beschreibung enthalten.

#### So wendest du Filter an:

1. Öffne die Datei `config/.env` in einem Texteditor
2. Suche nach der Zeile mit `SEARCH_TEXT=`
3. Füge deine Suchbegriffe durch Kommas getrennt hinzu, z.B.:
   ```
   SEARCH_TEXT=TM2,Atemschutz,Truppmann,Sprechfunk
   ```
4. Speichere die Datei

### E-Mail-Konfiguration

In der `.env` Datei kannst du die E-Mail-Konfiguration anpassen:

```
# E-Mail-Konfiguration
SENDER_EMAIL=sender@example.de
# Mehrere Empfänger können durch Kommas getrennt werden
RECIPIENT_EMAIL=erster.empfaenger@example.de,zweiter.empfaenger@example.com

# E-Mail-Archivierung
SAVE_EMAILS=True  # Auf True setzen, um E-Mails zu speichern
SAVE_EMPTY_EMAILS=True  # Auf False setzen, um leere E-Mails nicht zu speichern
EMAIL_ARCHIVE_DIR=data/email_archive  # Verzeichnis für gespeicherte E-Mails als Text
```

#### So fügst du mehrere E-Mail-Empfänger hinzu:

1. Öffne die Datei `config/.env` in einem Texteditor
2. Suche nach der Zeile mit `RECIPIENT_EMAIL=`
3. Füge mehrere E-Mail-Adressen durch Kommas getrennt hinzu, z.B.:
   ```
   RECIPIENT_EMAIL=erster.empfaenger@example.de,zweiter.empfaenger@example.com,dritter.empfaenger@example.com
   ```
4. Speichere die Datei

- **Mehrere Empfänger**: Du kannst mehrere E-Mail-Empfänger durch Kommas getrennt angeben.
- **E-Mail-Archivierung**: Alle gesendeten E-Mails werden als Textdateien im `EMAIL_ARCHIVE_DIR` Verzeichnis gespeichert.
- **Leere E-Mails**: Du kannst festlegen, ob auch E-Mails ohne neue Lehrgänge archiviert werden sollen.

## SMTP-Anmeldedaten einrichten

Du kannst die SMTP-Anmeldedaten auf zwei Arten konfigurieren:

1. **Umgebungsvariablen** in der `.env` Datei:
   ```
   SMTP_USERNAME=deine.email@example.de
   SMTP_PASSWORD=dein_passwort
   ```

2. **Verschlüsselte Credentials** (sicherer):
   ```
   python src/utils/setup_smtp_credentials.py
   ```
   Folge den Anweisungen, um deine SMTP-Anmeldedaten sicher zu speichern.

## Verwendung

### Einfache Ausführung

Um das System einmalig auszuführen, verwende das kombinierte Skript:

```
python bin/run_monitor_and_notify.py
```

Dieses Skript führt nacheinander den Monitor und den Mail-Notifier aus, um neue Lehrgänge zu finden und Benachrichtigungen zu senden.

### Einzelne Komponenten

Du kannst die Programme auch einzeln ausführen:

1. **Nur Daten aktualisieren**:
   ```
   python bin/monitor.py
   ```

2. **Nur Benachrichtigungen senden**:
   ```
   python bin/mail_notifier.py
   ```

### Automatisierte Ausführung

Für eine regelmäßige Ausführung kannst du einen Cronjob einrichten:

```
# Beispiel für einen Cronjob, der stündlich ausgeführt wird
0 * * * * cd /pfad/zum/projekt && python bin/run_monitor_and_notify.py >> logs/cron.log 2>&1
```

## Ordnerstruktur

```
.
├── bin/                    # Ausführbare Skripte
│   ├── monitor.py          # Hauptskript zum Abrufen der Lehrgangsdaten
│   ├── mail_notifier.py    # Skript zum Senden von E-Mail-Benachrichtigungen
│   └── run_monitor_and_notify.py  # Kombiniertes Skript für die automatisierte Ausführung
│
├── config/                 # Konfigurationsdateien
│   ├── .env                # Konfigurationsdatei mit Umgebungsvariablen
│   └── .env.example        # Beispielkonfiguration
│
├── data/                   # Datendateien
│   ├── termine.json        # Enthält alle gefundenen Lehrgänge
│   ├── last_sent.json      # Enthält die Lehrgänge, für die bereits Benachrichtigungen gesendet wurden
│   └── email_archive/      # Archiv aller gesendeten E-Mails als Textdateien
│
├── logs/                   # Protokolldateien
│   ├── mail_notifier.log   # Protokoll des Mail-Notifiers
│   └── run_monitor_and_notify.log  # Protokoll des kombinierten Skripts
│
└── src/                    # Quellcode
    ├── utils/              # Hilfsfunktionen und -klassen
    │   ├── credential_manager.py  # Klasse für die sichere Verwaltung der Anmeldedaten
    │   └── setup_smtp_credentials.py  # Hilfsskript zum Einrichten der SMTP-Anmeldedaten
    └── ...
```

## E-Mail-Format

Die E-Mail-Benachrichtigungen werden sowohl im Text- als auch im HTML-Format gesendet. Die HTML-Version enthält eine schön formatierte Tabelle mit allen Lehrgangsdetails:

- **Kursname**: Name des Lehrgangs
- **Termin**: Zeitraum des Lehrgangs (z.B. "10.10.2025 - 25.10.2025")
- **Status**: Status des Lehrgangs (z.B. "eingeladen", "geplant")
- **Ort**: Veranstaltungsort mit Adresse

## Protokollierung

Das System erstellt folgende Protokolldateien im `logs/` Verzeichnis:

- **monitor.log**: Protokoll des Monitor-Skripts
- **mail_notifier.log**: Protokoll des Mail-Notifiers
- **run_monitor_and_notify.log**: Protokoll des kombinierten Skripts

## Fehlerbehebung

Wenn keine E-Mails gesendet werden:

1. Überprüfe die Protokolldateien `mail_notifier.log` und `run_monitor_and_notify.log`
2. Stelle sicher, dass die SMTP-Anmeldedaten korrekt sind
3. Überprüfe, ob neue Lehrgänge in `termine.json` vorhanden sind
4. Vergleiche `termine.json` mit `last_sent.json`, um zu sehen, ob es tatsächlich neue Lehrgänge gibt