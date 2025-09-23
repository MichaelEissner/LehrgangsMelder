# Installationsanleitung für Website Monitor

Diese Anleitung führt Sie durch die Installation und Einrichtung des Website Monitors.

## Voraussetzungen

- Python 3.7 oder höher
- Pip (Python-Paketmanager)
- Internetzugang für die Installation der Abhängigkeiten

## Schritt 1: Python-Abhängigkeiten installieren

Öffnen Sie eine Kommandozeile (Terminal/CMD) im Projektverzeichnis und führen Sie folgenden Befehl aus:

```bash
pip install -r requirements.txt
```

Dies installiert alle benötigten Bibliotheken:
- requests: Für HTTP-Anfragen
- beautifulsoup4: Für HTML-Parsing
- cryptography: Für die Verschlüsselung der Credentials
- python-dotenv: Für das Laden von Umgebungsvariablen

## Schritt 2: Konfiguration einrichten

### Option 1: Setup-Tool verwenden (empfohlen)

Führen Sie das Setup-Tool aus, um die Konfiguration interaktiv einzurichten:

```bash
python setup_credentials.py
```

Folgen Sie den Anweisungen auf dem Bildschirm, um:
1. Website-Credentials einzurichten
2. SMTP-Credentials für Strato einzurichten
3. Die Konfigurationsdatei (.env) zu erstellen

### Option 2: Manuelle Konfiguration

1. Kopieren Sie die Beispiel-Umgebungsdatei:

```bash
cp .env.example .env
```

2. Bearbeiten Sie die `.env`-Datei und tragen Sie Ihre Konfigurationswerte ein.

3. Führen Sie das Programm einmal aus, um die Credentials interaktiv einzugeben:

```bash
python website_monitor.py
```

## Schritt 3: Programm testen

Führen Sie die Tests aus, um sicherzustellen, dass alles korrekt funktioniert:

```bash
python test_website_monitor.py
```

## Schritt 4: Programm ausführen

Starten Sie das Programm mit:

```bash
python website_monitor.py
```

## Fehlerbehebung

### ImportError für cryptography

Falls Sie eine Fehlermeldung wie `ImportError: No module named 'cryptography'` erhalten, versuchen Sie:

```bash
pip install cryptography --upgrade
```

Auf manchen Systemen benötigen Sie möglicherweise zusätzliche Entwicklungsbibliotheken:

**Auf Ubuntu/Debian:**
```bash
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev
pip install cryptography
```

**Auf Windows:**
Stellen Sie sicher, dass Sie die aktuelle Version von pip haben:
```bash
python -m pip install --upgrade pip
pip install cryptography
```

### SMTP-Verbindungsprobleme

Wenn Sie Probleme mit der SMTP-Verbindung zu Strato haben:

1. Überprüfen Sie, ob Ihre Strato-Zugangsdaten korrekt sind
2. Stellen Sie sicher, dass der SMTP-Server und Port korrekt sind (standardmäßig smtp.strato.de:587)
3. Prüfen Sie, ob Ihr Netzwerk ausgehende Verbindungen auf Port 587 erlaubt