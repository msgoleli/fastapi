# Projektplan

## Ziel

Eine lokal startbare FastAPI-Anwendung für einen Bücherkatalog. Ein Buch ist der
Aggregate Root und verweist auf eigenständig verwaltete Autoren und Verlage.

## Arbeitspakete

| Arbeitspaket | Ergebnis | Stand | Nächster Schritt |
| --- | --- | --- | --- |
| Domänenmodell | Buch, Autor, Verlag und Buch-Autor-Zuordnung | Implementiert | Modelltests ausführen |
| REST und GraphQL | Bücherkatalog lesen und pflegen | Implementiert | API-Tests ausführen |
| PostgreSQL | Datenbank und Schema `buch` | Konfiguriert | Compose-Setup mit leerem Volume prüfen |
| Anmeldung | Keycloak, Bearer-Token und Admin-Rolle | Konfiguriert | Schreibzugriff lokal mit Keycloak prüfen |
| Bruno | REST- und GraphQL-Requests | Angelegt | Requests gegen laufenden Server ausführen |
| Lasttest | Locust-Tasks für Bücher, Autoren und Verlage | Angepasst | Lasttest lokal durchführen |
| Qualitätssicherung | Ruff, ty, Pyrefly, pytest und MkDocs in GitHub Actions | Eingerichtet | Ersten Workflow-Lauf auf GitHub prüfen |
| Abhängigkeitsprüfung | uv-Audit und OWASP Dependency-Check | Eingerichtet | Bericht und Treffer bewerten |
| Dokumentation | API-, Architektur- und Projektunterlagen | Vorhanden | Nach Tests aktualisieren |

## Abschlusskriterien

- `uv run buch` startet die Anwendung mit einer eingerichteten PostgreSQL-Datenbank.
- REST- und GraphQL-Lesezugriffe funktionieren.
- Schreibzugriffe ohne Token liefern `401`; Schreibzugriffe mit Admin-Token sind
  erfolgreich.
- `uv run pytest`, Ruff, beide Typprüfungen und der MkDocs-Build laufen erfolgreich.
- GitHub Actions ist auf dem Branch `buch` erfolgreich.
- Bruno-Requests und Locust laufen gegen den lokalen Bücherkatalog.

## Risiken und Voraussetzungen

- Keycloak-Realm, Client und Rolle `admin` müssen lokal eingerichtet sein.
- Vorhandene PostgreSQL-Volumes werden nicht automatisch auf Datenbank und Schema
  `buch` migriert.
- Für die finale Abnahme müssen Tests und Lasttest ausgeführt werden. Ergebnisse
  werden erst nach dem tatsächlichen Lauf als erledigt markiert.
