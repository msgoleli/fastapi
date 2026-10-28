# Hinweise zu locust

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

## locust

_locust_ ist - neben _k6_ - ein weit verbreitetes Werkzeug für Lasttests und wird
eingesetzt, um Anwendungen z.B. in einer Cloud unter Last zu testen. Die Skripte werden
in Python implementiert.

## Vorbereitung

Der Lasttest verwendet die Lese-Endpunkte der Buch-API. Für aussagekräftige
Ergebnisse sollten vorher Bücher, Autoren und Verlage angelegt sein. PostgreSQL,
Keycloak und die App müssen laufen.

## Aufruf

Der Aufruf von _locust_ erfolgt durch folgendes Kommando:

```shell
  uv run locust -f tests/lasttest/locustfile.py
```

## Konfiguration und Start

Mit dem Aufruf von _locust_ wurden ein Webserver gestartet und in einem Webbrowser kann
man die URL `http://localhost:8089` aufrufen. In der Administrationsoberfläche setzt man
z.B. folgende Einstellungen:

- Number of users: `50`
- Ramp Up (users started/second): `5`
- Host: `https://localhost:8000`

Jetzt kann man den Button _Start_ anklicken.

Das Locust-Skript meldet sich mit dem lokalen Keycloak-Admin an und erzeugt Last auf
`/rest/buecher`, `/rest/autoren` und `/rest/verlage`.

## Interpretation der Ergebnisse

Bei der Interpretation möge man bedenken:

- Die Server-Infrastruktur besteht aus einem _Notebook_ und ist keine Server-Hardware.
- Auf dem Notebook läuft nicht nur der Appserver, sondern auch der _DB-Server_,
  _Keycloak-Server_, _Mailserver_ und der _Webserver für locust_.
- Sowohl der Appserver als auch die Backend-Server lauften _virtualisiert_ in einem
  _Container_.
- Die Container sind über ein virtuelles Netzwerk verbunden.
- Es wird _HTTPS_ genutzt und nicht nur HTTP.
- Spätestens jetzt wird klar, warum _web.de_ in ihren Anfangsjahren fast alles
  mit Python realisiert hat.
