# Installation des Beispiels

> Copyright 2026 - present [Jürgen Zimmermann](mailto:Juergen.Zimmermann@h-ka.de), Hochschule Karlsruhe
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

## Voraussetzung

Die Installation des Beispiels setzt voraus, dass _Python_ installiert ist, z.B. für
Windows von `https://www.python.org/downloads/windows`; der _install manager_ wird
**NICHT** benötigt. Für macOS gibt es z.B. `https://www.python.org/downloads/macos`.
Ob Python erfolgreich installiert ist, kann man folgendermaßen überprüfen:

```shell
    python --version
```

Evtl. muss man bei Windows noch die beiden Pfade `C:\<INSTALLATIONSVERZEICHNIS>`
und `C:\<INSTALLATIONSVERZEICHNIS>\Scripts` in die Umgebungsvariable `PATH`
aufnehmen.

### Rust und Cargo für Source-Code-Distributionen

Die Umgebungsvariable `CARGO_HOME` setzt man z.B. auf C:\Zimmermann\cargo und
ergänzt die Umgebungsvariable `PATH` um %CARGO_HOME%\bin. Danach lädt man sich
von https://rustup.rs die Datei `rustup-init.exe` herunter und führt sie aus.

## Installation von uv als Projektmanager

```shell
    # Windows:
    powershell -ExecutionPolicy ByPass -c 'Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression'

    # macOS/Linux:
    curl -LsSf https://astral.sh/uv/install.sh | sh
```

Danach ergänzt man die Umgebungsvariable `PATH` bei Windows um den Eintrag
`$env:USERPROFILE\.local\bin` und bei macOS sowie Linux um `$HOME/.local/bin`.
In einer _neuen_ Shell kann man dann z.B. `uv --version` aufrufen.

## Abhängigkeiten installieren und implizit .venv erstellen

```shell
    uv sync --all-groups
```

## Backend-Server

Vor dem Start des Appservers müssen die Backend-Server für PostgreSQL, Keycloak und
Mailing gestartet sein. Zur Konfiguration gibt es im jeweiligen Unterverzeichnis eine
`ReadMe.md` Datei:

- PostgreSQL: `extras\compose\postgres\ReadMe.md`
- Keycloak: `extras\compose\keycloak\ReadMe.md`
- Mailing: `extras\compose\mailpit\ReadMe.md`

## Applikationsserver

Durch das Kommando `uv run patient` kann man den Server starten (siehe `project.scripts`
in `pyproject.toml`).

## Tests mit pytest

Die Unit- und Integrationstests werden folgendermaßen augerufen, nachdem der Appserver
gestartet ist:

```shell
    uv run pytest
```

## Bruno

Mit _Bruno_ und der Collections in `extras\bruno\patient` kann nun die REST- und
GraphQL-Schnittstelle des Applikationsservers benutzt werden.

## Docker Image

Ein _hardened_ Docker Image wird folgendermaßen gebaut:

```shell
    docker buildx bake
```

## Docker Container

Um einen Docker Container einschließlich der Backend-Server zu starten, die dann
natürlich noch nicht gestartet sein dürfen, setzt man folgende Kommandos ab:

```shell
    # Windows:
    cd extras\compose\patient

    # macOS/Linux:
    cd extras/compose/patient

    docker compose up
```

## Dokumentation

Um die Dokumentation auf Basis von _mkdocs_ als Webserver zu starten, darf der eigene
Applikationsserver nicht gestartet sein, weil _mkdocs_ ebenfalls den bei Python üblichen
Port `8000` nutzt. Den Server für _mkdocs_ startet man dann folgendermaßen:

```shell
    uv run mkdocs serve
```
