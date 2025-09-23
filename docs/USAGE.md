# Website Monitor - Benutzerhandbuch

Dieses Programm überwacht eine Website auf bestimmte Kurse und sendet eine E-Mail-Benachrichtigung, wenn diese gefunden werden.

## Konfiguration

### Anmeldedaten

Es gibt zwei Möglichkeiten, Anmeldedaten zu konfigurieren:

1. **Verschlüsselte Credentials** (empfohlen für Produktionsumgebungen):
   ```bash
   python src/setup_credentials.py
   ```
   Folgen Sie den Anweisungen, um Ihre Anmeldedaten sicher zu speichern.

### Website-Konfiguration

Bearbeiten Sie die `.env`-Datei, um die Website-Konfiguration anzupassen:

- `WEBSITE_URL`: Die Basis-URL der Website
- `LOGIN_URL`: Die URL der Login-Seite
- `TARGET_PAGE`: Die relative URL der Zielseite, die überwacht werden soll
- `SEARCH_TEXT`: Die Texte, nach denen gesucht werden soll (durch Kommas getrennt)

### E-Mail-Konfiguration

Bearbeiten Sie die `.env`-Datei, um die E-Mail-Konfiguration anzupassen:

```
SMTP_SERVER=smtp.strato.de
SMTP_PORT=587
SMTP_USERNAME=ihr_smtp_benutzername
SMTP_PASSWORD=ihr_smtp_passwort
SENDER_EMAIL=absender@example.com
RECIPIENT_EMAIL=empfaenger@example.com
```

Alternativ können Sie die SMTP-Anmeldedaten auch verschlüsselt speichern:

```bash
python src/setup_credentials.py --smtp
```

## Ausführung

Führen Sie das Programm mit folgendem Befehl aus:

```bash
python src/website_monitor.py
```
## Funktionsweise

Das Programm führt folgende Schritte aus:

1. Einlesen der Konfiguration aus der `.env`-Datei
2. Entschlüsseln der gespeicherten Anmeldedaten
3. Anmelden auf der Website
4. Navigation zur Zielseite
5. Überprüfen des Inhalts auf die gesuchten Texte
6. Extrahieren detaillierter Informationen zu gefundenen Lehrgängen
7. Speichern gefundener Lehrgänge in JSON-Dateien im Ordner `gefundene_lehrgaenge/`
8. Vergleichen mit bereits gefundenen Lehrgängen
9. Senden einer E-Mail-Benachrichtigung nur für neu gefundene Lehrgänge


## Fehlerbehebung

### Inhaltserkennung

Wenn die gesuchten Texte nicht gefunden werden:

1. Überprüfen Sie die Suchtexte in der `.env`-Datei (durch Kommas getrennt)
2. Schauen Sie in die Debug-Datei `target_page_debug.html`
3. Versuchen Sie, kürzere oder allgemeinere Suchtexte zu verwenden
4. Stellen Sie sicher, dass die Suchtexte genau mit den Texten in der Tabelle übereinstimmen

## Debug-Dateien und Logging

### Debug-Modus

Das Programm kann im Debug-Modus ausgeführt werden, um detaillierte Informationen zu erhalten. Setzen Sie dazu die Umgebungsvariable `DEBUG` auf `True`:

```
DEBUG=True
```

### Logging-Level

## Speicherung gefundener Lehrgänge

Das Programm speichert Informationen über gefundene Lehrgänge im Ordner `gefundene_lehrgaenge/`. Für jeden gefundenen Lehrgang wird eine JSON-Datei erstellt, die folgende Informationen enthält:

- Lehrgangsname
- Datum und Uhrzeit
- Ort
- Verfügbare Plätze
- Zeitpunkt der Entdeckung

Diese Speicherung dient zwei Zwecken:
1. Vermeidung doppelter E-Mail-Benachrichtigungen für bereits gefundene Lehrgänge
2. Nachverfolgung, welche Lehrgänge bereits entdeckt wurden

Bei jedem Programmlauf werden neu gefundene Lehrgänge mit den bereits gespeicherten verglichen. Nur für Lehrgänge, die noch nicht in den Dateien gespeichert sind, werden E-Mail-Benachrichtigungen gesendet.

Sie können den Detailgrad der Logs mit der Umgebungsvariable `LOG_LEVEL` steuern:

```
LOG_LEVEL=DEBUG  # Sehr detaillierte Logs
LOG_LEVEL=INFO   # Standard-Informationen (Standardwert)
LOG_LEVEL=WARNING  # Nur Warnungen und Fehler
LOG_LEVEL=ERROR  # Nur Fehler
```

Das Programm schreibt Logs in die Datei `website_monitor.log` und gibt sie auch auf der Konsole aus.

## Sicherheit

Das Programm löscht automatisch alle Cookies beim Beenden, auch in Fehlerfällen. Dies verhindert, dass alte Sessions bestehen bleiben und potenzielle Sicherheitsrisiken darstellen.