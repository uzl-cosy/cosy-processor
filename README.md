# CoSy Device Application

Willkommen zu "Mein Python-Projekt"! Dieses README führt Sie durch die Installation und Ausführung des Projekts. Folgen Sie diesen Schritten, um die Umgebung einzurichten und das Projekt zu starten.

## Voraussetzungen

Stellen Sie sicher, dass Sie Python auf Ihrem System installiert haben. Dieses Projekt wurde mit Python 3.12 getestet.

## Installation

### Schritt 1: pipx installieren

`pipx` ermöglicht die Installation von Python-Paketen in isolierten Umgebungen. Installieren Sie `pipx`, falls noch nicht geschehen, indem Sie den folgenden Befehl in Ihrem Terminal ausführen:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

### Schritt 2: Poetry installieren

Nachdem `pipx` installiert ist, verwenden Sie es, um `poetry` zu installieren:

```bash
pipx install poetry
```

### Schritt 3: Poetry-Umgebung für Python 3.12 aktivieren

Aktivieren Sie die passende Poetry-Umgebung für Python 3.12:

```bash
poetry env use 3.12
```

### Schritt 4: Abhängigkeiten installieren

Installieren Sie die Projekt-Abhängigkeiten mit `poetry`:

```bash
poetry install
```

## Ausführung

Nach der Installation der Abhängigkeiten können Sie das Hauptskript des Projekts auf zwei Arten ausführen:

### Option 1: Direkte Ausführung

```bash
poetry run main
```

### Option 2: Ausführung im Python Debugger in VSCode

1. Öffnen Sie VSCode.
2. Starten Sie den Debugger mit der Konfiguration `cosy` bzw. der sich im Projektverzeichnis befindlichen `launch.json`.
