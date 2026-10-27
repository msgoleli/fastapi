# Entwicklung des Bücherkatalogs mit Cursor

## Projekt und Ziel

Der Bücherkatalog ist eine FastAPI-Anwendung zur Verwaltung von Büchern, Autoren und
Verlagen. Diese Dokumentation beschreibt, wie Cursor bei der Arbeit an diesem
Software-Engineering-Projekt eingesetzt werden kann: beim Einrichten der Umgebung,
beim Verstehen des vorhandenen Codes, bei Änderungen und bei deren Prüfung.

Cursor basiert auf Visual Studio Code und ergänzt die gewohnte Editor-Umgebung um
integrierte KI-Funktionen. Der Vergleich im letzten Abschnitt bezieht sich auf den
Entwicklungsablauf in diesem Projekt; welche Umgebung besser passt, hängt von den
Anforderungen und der vorhandenen Konfiguration ab.

## 1. Installation

Cursor für Windows wird über die [offizielle Downloadseite](https://cursor.com/download)
heruntergeladen und mit dem Installationsprogramm eingerichtet. Beim ersten Start
können Einstellungen aus Visual Studio Code übernommen werden. Für die integrierten
KI-Funktionen ist eine Anmeldung erforderlich.

Nach der Installation wird der Projektordner über **File → Open Folder** geöffnet.
Cursor sollte auf den Repository-Ordner zeigen, damit die Suche und der Agent auch
Dateien aus Tests, Konfiguration und Dokumentation als Kontext finden können.

## 2. Erweiterungen

VS-Code-Erweiterungen können importiert oder bei Bedarf neu installiert werden. Die
Verfügbarkeit unterscheidet sich teilweise, da Cursor einen Open-VSX-basierten
Erweiterungskatalog verwendet. Für dieses Python-Projekt sind folgende Erweiterungen
sinnvoll:

- **Python** für Sprachunterstützung und Interpreter-Auswahl.
- **Ruff** für Linting und Formatierung; Ruff ist im Projekt bereits konfiguriert.
- **Docker** für die Compose- und Container-Konfiguration.
- **Markdown** für die Projekt- und API-Dokumentation.

Eine Erweiterung sollte nur installiert werden, wenn sie im Projekt gebraucht wird.
Herausgeber und benötigte Berechtigungen sollten vor der Installation geprüft werden.
Weitere Hinweise enthält die [Cursor-Dokumentation zu Erweiterungen](https://cursor.com/help/customization/extensions).

## 3. Projekt einrichten

Das Projekt benötigt Python 3.14 oder neuer und `uv`. Im integrierten Terminal werden
die Abhängigkeiten installiert und die virtuelle Umgebung angelegt:

```shell
uv sync
```

Anschließend wird in Cursor der Python-Interpreter aus `.venv` ausgewählt. Unter
Windows befindet er sich üblicherweise unter `.venv\Scripts\python.exe`.

Die wichtigsten Einstiegspunkte im Quellcode sind:

| Bereich | Datei | Aufgabe |
| --- | --- | --- |
| FastAPI-Anwendung | `src/buch/fastapi_app.py` | Erstellt die App und bindet Router ein |
| Buch-API | `src/buch/router/buch_router.py` | REST-Endpunkte und Eingabe-/Ausgabemodelle |
| Datenzugriff | `src/buch/repository/buch_repository.py` | Lädt und speichert Buch-Aggregate |
| Datenmodell | `src/buch/entity/buch.py` | ORM-Modell für Buch und Autorenbeziehung |
| API-Tests | `tests/catalog/test_book_api.py` | Prüft REST- und GraphQL-Verhalten |

Die Anwendung kann mit der lokalen Entwicklungsvariante gestartet werden:

```shell
uv run uvicorn buch.fastapi_app:app --app-dir src --reload
```

Für den vollständigen Betrieb wird die PostgreSQL- und Keycloak-Umgebung aus der
Projekt-README benötigt. Die Katalogtests verwenden dagegen eine isolierte
SQLite-Datenbank.

## 4. Mit Cursor im Projekt arbeiten

### Codebasis erschließen

Vor einer Änderung kann der Agent gebeten werden, den Aufbau zu erklären und nur
relevante Dateien zu nennen:

> Erkläre den Ablauf eines `GET /rest/buecher`-Aufrufs. Verfolge ihn vom Router bis
> zum Repository und nenne die zugehörigen Tests. Ändere keine Dateien.

So lässt sich die vorgeschlagene Änderung in die bestehende Struktur einordnen, bevor
Code geändert wird. Dateien wie `@src/buch/router/buch_router.py` können direkt als
Kontext angegeben werden.

### Tab-Vervollständigung

Cursor Tab schlägt Code während der Eingabe vor. Mit `Tab` wird ein Vorschlag
übernommen; mit `Escape` wird er verworfen. Mehrzeilige Vorschläge und Änderungen an
Imports sollten vor der Übernahme zusammen mit dem umgebenden Code geprüft werden.
Details stehen in der [Cursor-Dokumentation zu Tab](https://cursor.com/help/ai-features/tab).

### Chat und Agent

Der Chat eignet sich, um Code erklären zu lassen oder eine Fehlermeldung einzugrenzen.
Der Agent kann zusätzlich Änderungen über mehrere Dateien vorschlagen und
Projektbefehle ausführen. Cursor bezeichnet den früheren Composer-Arbeitsablauf in
der aktuellen Dokumentation als Agent. Unter Windows öffnet `Ctrl+I` den Agent; die
Tastenkürzel können angepasst werden.

Für größere Änderungen sollte zuerst ein Plan angefordert werden. Danach wird der
Plan mit den Anforderungen verglichen; erst dann wird die Implementierung beauftragt.
Nach der Bearbeitung wird der vollständige Diff geprüft. Eine kurze Aufgabenbeschreibung
mit Ziel, betroffenen Dateien und Randbedingungen liefert meist passendere Änderungen
als eine offene Aufforderung wie „verbessere den Code“.

## 5. Beispiele am Bücherkatalog

### Neue Route: Bücher nach Genre

Das Datenmodell enthält bereits das Pflichtattribut `genre` mit einer Länge von 1 bis
100 Zeichen. Die Antwort der Buch-API gibt das Genre ebenfalls zurück. Die vorhandene
Buchliste `GET /rest/buecher` akzeptiert derzeit den Parameter `q`, der nach dem Titel
filtert. Eine Route zum Abrufen von Büchern nach Genre ist im aktuellen Projektstand
noch nicht vorhanden.

Als neue Route bietet sich `GET /rest/buecher/genre/{genre}` an. Dafür sind der Router,
die Repository-Abfrage und die API-Tests relevant. Eine mögliche Anfrage an den
Composer beziehungsweise Agent lautet:

> Ergänze `GET /rest/buecher/genre/{genre}`. Die Route soll Bücher des angegebenen
> Genres zurückgeben und dabei dieselbe Ausgabe wie die bestehende Buchliste nutzen.
> Ergänze den passenden Repository-Zugriff und API-Tests für Treffer, ein unbekanntes
> Genre und eine leere Datenbank. Folge der bestehenden Schichtenstruktur und ändere
> keine anderen Funktionen.

Der Diff sollte zeigen, dass die neue Route, der Datenzugriff und die Tests zur
vorhandenen Architektur passen. Die bestehende Suche über `q` bleibt davon unberührt.

### Fehler mit Chat untersuchen

Bei einem echten Fehler werden die Fehlermeldung, der betroffene Endpunkt und der
Reproduktionsschritt an den Chat gegeben. Zunächst sollte nach einer Erklärung und
einer wahrscheinlichen Ursache gefragt werden, ohne Dateien zu ändern. Erst wenn die
Ursache nachvollziehbar ist, wird eine gezielte Korrektur angefordert. Damit bleibt
die Diagnose überprüfbar und unnötige Änderungen werden vermieden.

### Tests ergänzen

Tests können anhand der bestehenden Struktur vorgeschlagen und danach einzeln geprüft
werden. Für die neue Genre-Route sollten mindestens diese Fälle abgedeckt sein:

- ein vorhandenes Genre liefert die dazugehörigen Bücher;
- ein unbekanntes Genre liefert eine leere Liste;
- eine leere Datenbank liefert eine leere Liste.

Der vorhandene API-Test unter `tests/catalog/test_book_api.py` zeigt, wie Testdaten
angelegt und Endpunkte mit dem FastAPI-TestClient aufgerufen werden.

### Projektprüfungen

Die Katalogtests und statischen Prüfungen werden im Projektterminal ausgeführt:

```shell
uv run pytest tests/catalog
uv run ruff check src/buch tests/catalog
uv run ruff format --check src/buch tests/catalog
uv run ty check src/buch tests/catalog
```

Das Ergebnis jeder Prüfung gehört zur Bewertung der Änderung. Ein erfolgreicher Test
belegt die geprüften Fälle, ersetzt aber nicht die inhaltliche Prüfung des Diffs.

## 6. Visual Studio Code und Cursor

| Aspekt | Visual Studio Code | Cursor |
| --- | --- | --- |
| Grundlage | Erweiterbarer Code-Editor | Basiert auf Visual Studio Code und integriert zusätzliche KI-Arbeitsabläufe |
| Erweiterungen | Microsoft Marketplace | Open-VSX-basierter Katalog; einzelne Erweiterungen können abweichen |
| KI-Unterstützung | Über verfügbare integrierte Funktionen und Erweiterungen | Tab-Vervollständigung sowie Chat- und Agent-Funktionen |
| Übernahme vorhandener Einstellungen | Bereits eingerichtet, wenn VS Code verwendet wird | Import von VS-Code-Einstellungen ist möglich |
| Arbeitsweise | Aufgaben werden typischerweise manuell oder mit installierten Erweiterungen bearbeitet | Code kann zusätzlich mit Projektkontext erklärt, vorgeschlagen und geändert werden |

Beide Editoren können für Python und FastAPI verwendet werden. Cursor bringt KI-Funktionen
direkt in den Editor; Visual Studio Code bietet eine größere Auswahl an Erweiterungen
aus dem Microsoft Marketplace. Für den Bücherkatalog hängt die Wahl davon ab, welche
Erweiterungen verfügbar sind und wie stark KI-Unterstützung im Entwicklungsablauf
genutzt werden soll.

## 7. Qualitäts- und Sicherheitsaspekte

KI-Vorschläge sind zu prüfen, bevor sie übernommen werden. Das gilt besonders für
Authentifizierung, Rollenprüfungen, Datenbankzugriffe und Eingabevalidierung. Tokens,
Passwörter und private Schlüssel gehören weder in Prompts noch in Versionskontrolle.
Projektregeln können wiederkehrende Konventionen festhalten; Cursor unterstützt dafür
`.cursor/rules/` und `AGENTS.md`. Sie ersetzen keine Codeprüfung und keine Tests.

## Quellen

- [Cursor herunterladen und installieren](https://cursor.com/help/getting-started/install)
- [Von Visual Studio Code migrieren](https://docs.cursor.com/get-started/migrate-from-vs-code)
- [Erweiterungen in Cursor](https://cursor.com/help/customization/extensions)
- [Tab-Vervollständigung](https://cursor.com/help/ai-features/tab)
- [Agent-Modus](https://cursor.com/help/ai-features/agent)
- [Projektregeln](https://cursor.com/help/customization/rules)
