# Bücherkatalog

FastAPI-Anwendung zur Verwaltung von Büchern, Autoren und Verlagen. Ein Buch ist der
Aggregate Root: die Buch-API ändert die Buchdaten und die Zuordnung zu vorhandenen
Autoren und einem vorhandenen Verlag in einer Transaktion. Autoren und Verlage werden
als eigenständige Referenzen verwaltet.

## Starten

Voraussetzung ist eine erreichbare PostgreSQL-Datenbank entsprechend
`src/buch/config/resources/app.toml`. Die Tabellen werden beim Anwendungsstart aus
den SQLAlchemy-Modellen erstellt.

```shell
uv sync
uv run buch
```

Der Befehl `uv run buch` startet den vorkonfigurierten Uvicorn-Server mit TLS.
Alternativ lässt sich die App für die lokale Entwicklung ohne TLS mit
`uv run uvicorn buch.fastapi_app:app --app-dir src --reload` starten. OpenAPI ist unter
`https://localhost:8000/docs`, GraphiQL unter `/graphql`, Metriken unter `/metrics`
und Health unter `/health/liveness` sowie
`/health/readiness` verfügbar. Anmeldung erfolgt über den vorhandenen Keycloak-Endpunkt
`/auth/token`; Schreibzugriffe benötigen ein Token mit der Rolle `ADMIN`.

## REST

Alle REST-Routen haben das Präfix `/rest`.

| Methode | Route | Zweck |
| --- | --- | --- |
| GET | `/buecher?q=...` | Bücher auflisten und nach Titel filtern |
| GET | `/buecher/{id}` | Buch mit Verlag und Autoren lesen |
| POST | `/buecher` | Buch anlegen |
| PUT | `/buecher/{id}` | Buchdaten und Verknüpfungen ersetzen |
| DELETE | `/buecher/{id}` | Buch löschen |
| GET/POST | `/autoren` | Autoren auflisten/anlegen |
| GET/PUT/DELETE | `/autoren/{id}` | Autor lesen, ändern, löschen |
| GET/POST | `/verlage` | Verlage auflisten/anlegen |
| GET/PUT/DELETE | `/verlage/{id}` | Verlag lesen, ändern, löschen |

POST, PUT und DELETE benötigen `Authorization: Bearer <token>` mit der Rolle `ADMIN`.
Die GET-Endpunkte sind öffentlich lesbar.

Beispiel für `POST /rest/buecher`:

```json
{
  "titel": "Der Beispielroman",
  "isbn": "9781234567897",
  "erscheinungsdatum": "2024-03-15",
  "genre": "Roman",
  "verlag_id": 1,
  "autoren_ids": [1]
}
```

Eine Bruno-Collection mit Requests für Login, Autoren, Verlage und Bücher liegt unter
`extras/bruno/buch`. Hinweise zum Import und zum lokalen Admin-Token stehen in
`extras/bruno/ReadMe.md`.

## GraphQL

GraphQL ist unter `/graphql` erreichbar. Queries: `buecher(titel)`, `buch(id)`,
`autoren` und `verlage`. Die Mutation `buchAnlegen(buch)` übernimmt dieselben
Buchdaten und Referenz-IDs wie die REST-API.

## Tests

Die aktuelle Katalogsuite liegt in `tests/catalog` und verwendet eine isolierte
SQLite-Datenbank. Die früheren Patiententests bleiben als Altbestand unter `tests/`
liegen, werden durch `testpaths` aber nicht mehr gesammelt.

```shell
uv run pytest
```

## Domäne

- **Buch**: Titel, eindeutige ISBN, Erscheinungsdatum, Genre, ein Verlag und mehrere
  Autoren.
- **Autor**: Vorname, Nachname und eindeutige E-Mail-Adresse; kann mehreren Büchern
  zugeordnet sein.
- **Verlag**: eindeutiger Name, Sitz und optionale Website; veröffentlicht mehrere
  Bücher.
- **buch_autor**: Zuordnungstabelle. Beim Löschen eines Buchs wird nur die Zuordnung
  entfernt, nicht die referenzierten Autor- oder Verlagsdatensätze.
