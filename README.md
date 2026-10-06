# Beispiel mit FastAPI, VS Code und Docker

> Copyright 2023 - present [Jürgen Zimmermann](mailto:Juergen.Zimmermann@h-ka.de), Hochschule Karlsruhe
>
> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU General Public License as published by
> the Free Software Foundation, either version 3 of the License, or
> at your option any later version
>
> This program is distributed in the hope that it will be useful
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
> GNU General Public License for more details
>
> You should have received a copy of the GNU General Public License
> along with this program. If not, see <https://www.gnu.org/licenses/>
>
> Preview in VS Code durch `<Strg><Shift>v`

Durch das Kommando `Get-Command python` kann man in der PowerShell überprüfen,
ob man zum Aufsetzen der virtuellen Umgebung die beabsichtigte .exe-Datei
verwendet, und mit `python --version` überprüft mandie Version von Python.

Zunächst legt man ein Verzeichnis an, z.B. `C:\workspace\python\fastapi`.
In einer Shell (PowerShell bei Windows oder bash bei macOS) ruft man folgende
Kommandos auf:

```shell
    # uv aktualisiert sich ggf. selbst
    uv self update

    # Packages aus pyproject.toml installieren: dependencies und alle "dependency-groups"
    uv sync --all-groups
```

Bei VS Code wählt man durch die Funktionstaste _F1_ man in der _Kommandopalette_ den
Eintrag _Python: Interpreter auswählen_ mit dem Unterpunkt `.\.venv\Scripts\python.exe`
aus. Siehe https://code.visualstudio.com/docs/python/environments
Dadurch wird der Python-Interpreter der virtuellen Umgebung verwendet, die mit
_uv_ angelegt wurde.

## Inhalt

- [Backend-Server](#backend-server)
- [Applikationsserver](#applikationsserver)
- [Testen](#testen)
  - [pytest](#pytest)
  - [Backend-Server und Appserver als Voraussetzung für Integrationstests](#backend-server-und-appserver-als-voraussetzung-für-integrationstests)
  - [pytest in der Kommandozeile](#pytest-in-der-kommandozeile)
  - [pytest mit VS Code](#pytest-mit-vs-code)
  - [locust für Lasttests](#locust-für-lasttests)
- [Statische Codeanalyse](#statische-codeanalyse)
  - [ruff, ty und pyrefly](#ruff-ty-und-pyrefly)
  - [SonarQube](#sonarqube)
- [Analyse von Sicherheitslücken](#analyse-von-sicherheitslücken)
  - [ruff zur Analyse von eigenen Sicherheitslücken](#ruff-zur-analyse-von-eigenen-sicherheitslücken)
  - [OWASP Dependency Check](#owasp-dependency-check)
  - [Docker Scout](#docker-scout)
- [Generierung der Dokumentation mit MkDocs](#generierung-der-dokumentation-mit-mkdocs)
- [Port bereits belegt?](#port-bereits-belegt)

## Backend-Server

Vor dem Start des Appservers müssen die Backend-Server für PostgreSQL, Keycloak und
Mailing gestartet sein. Zur Konfiguration gibt es im jeweiligen Unterverzeichnis eine
`ReadMe.md` Datei:

- PostgreSQL: `extras\compose\postgres\ReadMe.md`
- Keycloak: `extras\compose\keycloak\ReadMe.md`
- Mailing: `extras\compose\mailpit\ReadMe.md`

Wenn die Backend-Server eingrichtet sind, kann man sie mit _Docker Compose_ starten:

```shell
    # Windows
    cd .\extras\compose\backend

    # macOS / Linux
    cd ./extras/compose/backend

    docker compose up
```

## Applikationsserver

Durch das Kommando `uv run patient` kann man den Server starten (siehe `project.scripts`
in `pyproject.toml`). Dabei wird _uvicorn_ als ASGI-Server verwendet.

Die von _SQLAlchemy_ generierten SQL-Anweisungen werden mit _logging_ aus der
Python-Standardbibliothek protokolliert. Dadurch haben sie ein anderes Log-Format
als _loguru_ und fallen auch dementsprechend auf. Wenn man das Log-Format von
loguru auch bei SQLAlchemy haben möchte, so muss man den auskommentierten Code
in `src\patient\repository\session.py` aktivieren.

## Testen

### pytest

_pytest_ https://docs.pytest.org ist eine bessere Alternative zu _unittest_ aus der
Python-Distribution.

### Backend-Server und Appserver als Voraussetzung für Integrationstests

Vor dem Start der Integrationstests müssen DB-Server, Keycloak-Server und Appserver
gestartet sein. Der Mailserver sollte gestartet sein.

Die Integrationstests sind unterhalb von `tests` im Verzeichnis `integration`.
Durch jeweils ein _Fixture_ von pytest werden pro weiterem Unterverzeichnis (z.B. `rest`)
die (Test-) Datenbank und _Keycloak_ neu geladen.

### pytest in der Kommandozeile

Durch `uv run pytest` werden die Tests im Verzeichnis `tests` ausgeführt, weil das
Verzeichnis `tests` in `pyproject.toml` als Test-Verzeichnis deklariert ist.

Durch `uv run pytest --co` ("collect-only") kann man sich auflisten lassen, in
welcher Reihenfole die Tests ausgeführt werden.

Mit z.B. `uv run pytest -m get_request` startet man nur Test mit der Markierung
`get_request` oder man verwendet in `pyproject.toml` bei der Table `[tool.pytest.ini_options]`
die Property `addopts`.

Einzelne Testfunktionen, z.B. `test_get_by_id_admin` aus `get_by_id_test.px` im Verzeichnis
 `tests\integration\rest`:

```shell
    uv run pytest -k test_get_by_id_admin
```

### pytest mit VS Code

Zunächst klickt man in der Werkzeugleiste (am linken Rand) auf das _test beaker icon_,
das aussieht wie ein Becherglas bei einem chemischen Versuch, und klickt danach
auf den Menüpunkt _Configure Python Tests_. Nun wählt man der Reihe nach _pytest_
und _tests_ aus. Jetzt kann man die gewünchte(n) Testfunktion auswählen und
einschließlich der Fixtures starten.

Weitere Details siehe auch https://code.visualstudio.com/docs/python/testing.

### locust für Lasttests

Siehe `README.md` in `tests\lasttest`.

## Generierung der Dokumentation mit MkDocs

```shell
    # Eingebauten Webserver starten
    uv run mkdocs serve

    # Webbrowser öffnen mit http://localhost:8000

    # Nur HTML-Dokumentation generieren
    uv run mkdocs build
```

Als Starthilfe zum Aufsetzen von _MkDocs_ gibt es das Kommando `mkdocs new .`,
um im aktuellen Verzeichnis die Konfigurationsdatei `mkdocs.yaml` und im
Unterverzeichnis `doc` die Datei `index.md` anzulegen.

## Statische Codeanalyse

### ruff, ty und pyrefly

_ruff_ als Linter und _ty_ sowie _pyrefly_ als "Type Checker" werden als Tool für _uv_
folgendermaßen installiert:

```shell
    uv tool install ruff
    uv tool install ty
    uv tool install pyrefly
```

Danach kann man diese Werkzeuge folgendermaßen aufrufen:

```shell
    ruff check [--preview] src tests
    ruff format [--preview] src tests

    ty check src tests/unit tests/integration
    pyrefly check --output-format full-text [--verbose]
```

### SonarQube

Für eine statische Codeanalyse durch _SonarQube_ muss zunächst der
SonarQube-Server mit _Docker Compose_ als Docker-Container gestartet werden:

```shell
    # Windows
    cd extras\compose\sonarqube
    # macOS / Linux
    cd extras/compose/sonarqube

    docker compose up
```

Wenn der Server zum ersten Mal gestartet wird, ruft man in einem Webbrowser die
URL `http://localhost:9000` auf. In der Startseite muss man sich einloggen und
verwendet dazu als Loginname `admin` und ebenso als Password `admin`. Danach
wird man weitergeleitet, um das initiale Passwort zu ändern.

Nun wählt man in der Webseite rechts oben das Profil über _MyAccount_ aus und
klickt auf den Karteireiter _Security_. Im Abschnitt _Generate Tokens_ macht man
nun die folgende Eingaben:

- _Name_: z.B. Frameworks für Python
- _Type_: _Global Analysis Token_ auswählen
- _Expires in_: z.B. _90 days_ auswählen

Abschließend klickt man auf den Button _Generate_ und trägt den generierten
Token in der Datei `sonar-project.properties` für die Property `sonar.token` ein,
damit der Token im Skript `sonar-scanner.py` verwendet werden kann.

Nachdem der Server gestartet ist, wird der SonarQube-Scanner in einer zweiten
PowerShell mit `python sonar-scanner.py` gestartet. Das Resultat kann dann in der
Webseite des zuvor gestarteten Servers über die URL `http://localhost:9000`
inspiziert werden.

Abschließend wird der oben gestartete Server in einer 2. PowerShell heruntergefahren.

```shell
    # Windows
    cd extras\compose\sonarqube
    # macOS / Linux
    cd extras/compose/sonarqube

    docker compose down
```

## Analyse von Sicherheitslücken

### ruff zur Analyse von eigenen Sicherheitslücken

Da der Linter _ruff_ auch die Regeln von _bandit_ implementiert, erfolgt durch den Aufruf
von ruff eine implizite Analyse im Hinblick auf Sicherheitslücken.

### OWASP Dependency Check

Mit _OWASP Dependency Check_ werden alle in `pyproject.toml` installierten
Module mit den _CVE_-Nummern der NIST-Datenbank abgeglichen.

Von https://nvd.nist.gov/developers/request-an-api-key fordert man einen "API Key"
an, um im Laufe des Semesters mit _OWASP Dependency Check_ die benutzte Software
("3rd Party Libraries") auf Sicherheitslücken zu prüfen. Diesen API Key trägt
man in `.env` als Wert der Umgebungsvariablen `NVD_API_KEY` ein.

```shell
    uv run extras/dependency-check.py
```

### Sicherheitslücken in 3rd Party Packages

Zur Überprüfung von bekannten Sicherheitslücken in den verwendeten 3rd Party Packages
ruft man das Komando `uv audit` auf:

```shell
    uv audit
```

### Docker Scout

Mit dem Unterkommando `quickview` von _Scout_ kann man sich zunächst einen
groben Überblick verschaffen, wieviele Sicherheitslücken in den Bibliotheken im
Image enthalten sind:

```shell
    docker scout quickview juergenzimmermann/patient:2026.10.1-hardened
    docker scout quickview juergenzimmermann/patient:2026.10.1-trixie
    docker scout quickview juergenzimmermann/patient:2026.10.1-alpine
```

Dabei bedeutet:

- C ritical
- H igh
- M edium
- L ow

Sicherheitslücken sind als _CVE-Records_ (CVE = Common Vulnerabilities and Exposures)
katalogisiert: https://www.cve.org (ursprünglich: https://cve.mitre.org/cve).
Die Details zu den CVE-Records im Image kann man durch das Unterkommando `cves`
von _Scout_ auflisten:

```shell
    docker scout cves juergenzimmermann/patient:2026.10.1-hardened
    docker scout cves --format only-packages juergenzimmermann/patient:2026.10.1-hardened
```

Statt der Kommandozeile kann man auch den Menüpunkt "Docker Scout" im
_Docker Dashboard_ verwenden.

### Port bereits belegt?

Falls der Server nicht gestartet werden kann, weil z.B. der Port `3000` belegt ist,
kann man bei Windows in der Powershell zunächst die ID vom Betriebssystem-Prozess ermitteln,
der den Port belegt und danach diesen Prozess beenden:

```powershell
    netstat -ano | findstr ':3000'
    taskkill /F /PID <Prozess-ID>
```

Bei macOS:

```shell
    ps -af
    kill <Prozess-ID>
    # ggf.
    kill -9 <Prozess-ID>
```
