# Bruno-Collections

## Buch

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

Die API nutzt `https://127.0.0.1:8000`. `127.0.0.1` ist hier absichtlich statt
`localhost` eingetragen: `localhost` kann auf IPv6 (`::1`) zeigen, wo bei gleichzeitig
laufendem Docker- und lokalem Server ein anderer Dienst auf Port 8000 antwortet. Für
das lokale selbst-signierte Zertifikat muss
in Bruno die SSL/TLS-Zertifikatsprüfung deaktiviert sein (Preferences → SSL/TLS
Certificate Verification).

Im Environment `lokal` das Keycloak-Passwort als Secret eintragen. Zuerst den Request
**Token als Admin** mit Methode `QUERY` ausführen. Den zurückgegebenen Wert `token`
anschließend als Secret in die Environment-Variable `token` kopieren. Die Requests zum
Anlegen benötigen ein Token mit der Rolle `ADMIN`.

Die aktuelle lokale Datenbank enthält das Beispielbuch **GraphQL Beispielbuch** mit der
ISBN `9781234567811`; die QUERY-Beispiele suchen nach diesem Titel und der
Environment-Variable `suchIsbn`. Bei einer leeren Datenbank zuerst **Verlag anlegen**,
**Autor anlegen** und **Buch anlegen** der Reihe nach senden. Dann `suchIsbn` auf den Wert
von `isbn` setzen. Bei einer Neuanlage müssen Verlagname, E-Mail-Adresse und ISBN
eindeutig sein. Falls Verlag oder Autor andere IDs als `1` erhalten, im Environment
`lokal` die Variablen `verlagId` und `autorId` anpassen.

Im REST-Ordner **QUERY** liegen Beispiele für die benutzerdefinierte HTTP-Methode
`QUERY`. Sie verhält sich wie eine lesende Suche, überträgt die Suchkriterien aber als
JSON im Request-Body statt als URL-Query-Parameter. Die Suche ist öffentlich und benötigt
keinen Token.

Die GraphQL-Requests liegen im Ordner `GraphQL`. **Bücher abfragen** liest Bücher,
Autoren und Verlage. **Buch anlegen** benötigt ebenfalls den Admin-Token und die IDs
aus dem Environment. Für wiederholte Mutations muss die ISBN eindeutig geändert werden.

Die frühere Patient-Collection wurde unverändert unter `extras/bruno/patient-legacy`
aufbewahrt. Sie gehört nicht mehr zur Buch-API.
