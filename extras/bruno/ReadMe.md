# Bruno-Collections

## Buchkatalog

Die aktuelle Collection liegt in `extras/bruno/buch`. In Bruno **Open Collection** wählen
und diesen Ordner öffnen; danach das Environment `lokal` auswählen.

Für die lokale Quellcode-Version zuerst PostgreSQL, Keycloak und Mailpit starten
(im Projekt-Hauptordner):

```shell
docker compose -f extras/compose/backend/compose.yml up -d
uv run buch
```

`uv run buch` läuft dabei im Projekt-Hauptordner. So testest du den aktuellen lokalen
Code und nicht ein bereits gebautes Container-Image.

Die API nutzt `https://localhost:8000`. Für das lokale selbst-signierte Zertifikat muss
in Bruno die SSL/TLS-Zertifikatsprüfung deaktiviert sein (Preferences → SSL/TLS
Certificate Verification).

Im Environment `lokal` das Keycloak-Passwort als Secret eintragen. Zuerst den Request
**Token als Admin** mit Methode `QUERY` ausführen. Den zurückgegebenen Wert `token`
anschließend als Secret in die Environment-Variable `token` kopieren. Die Requests zum
Anlegen benötigen ein Token mit der Rolle `ADMIN`.

Danach **Verlag anlegen**, **Autor anlegen** und **Buch anlegen** der Reihe nach senden.
Bei erneutem Ausführen müssen Verlagname, E-Mail-Adresse und ISBN eindeutig geändert
werden. Falls Verlag oder Autor andere IDs als `1` erhalten, im Environment `lokal` die
Variablen `verlagId` und `autorId` anpassen.

Die GraphQL-Requests liegen im Ordner `GraphQL`. **Bücher abfragen** liest Bücher,
Autoren und Verlage. **Buch anlegen** benötigt ebenfalls den Admin-Token und die IDs
aus dem Environment. Für wiederholte Mutations muss die ISBN eindeutig geändert werden.

Die frühere Patient-Collection wurde unverändert unter `extras/bruno/patient-legacy`
aufbewahrt. Sie gehört nicht mehr zur Bücherkatalog-API.
