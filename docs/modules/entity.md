# Domänenmodell

- `Buch` ist Aggregate Root.
- `Autor` kann mehreren Büchern zugeordnet werden.
- `Verlag` veröffentlicht mehrere Bücher.
- Die Autorenzuordnung wird in `buch_autor` persistiert.

Implementierung: [Entity-Paket](https://github.com/msgoleli/fastapi/tree/buch/src/buch/entity).
