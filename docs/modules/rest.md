# REST-Schnittstelle

Die REST-Routen liegen unter `/rest`. Bücher werden über [buch_router.py](../../src/buch/router/buch_router.py)
als Aggregate Roots angelegt, gelesen, geändert und gelöscht. Autoren und Verlage
werden über [katalog_router.py](../../src/buch/router/katalog_router.py) verwaltet.
