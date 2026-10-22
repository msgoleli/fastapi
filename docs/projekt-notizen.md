# Projektnotizen

## Festgehaltene Entscheidungen

- `Buch` ist der Aggregate Root.
- Autoren und Verlage sind eigenständige Referenzen. Das Löschen eines Buchs löscht
  diese Referenzen nicht.
- REST- und GraphQL-Lesezugriffe sind öffentlich. Schreibzugriffe erfordern die
  Keycloak-Rolle `ADMIN`.
- Der Anwendungsdatenbankname und das Schema lauten `buch`.
- Die alte Patient-Bruno-Collection bleibt unter `extras/bruno/patient-legacy` als
  Referenz erhalten.

## Offene Punkte für die Abnahme

- GitHub Actions auf GitHub ausführen und Fehler beheben.
- PostgreSQL und Keycloak mit den lokalen Compose-Dateien starten.
- Login sowie REST- und GraphQL-Schreibzugriffe mit einem Admin-Token prüfen.
- Prüfen, ob bestehende PostgreSQL-Volumes neu eingerichtet werden müssen.
- Locust mit angelegten Beispieldaten starten und Ergebnisse notieren.

## Besprechungsnotizen

| Datum | Teilnehmende | Thema | Entscheidung / Aufgabe |
| --- | --- | --- | --- |
|  |  |  |  |
