# Datenzugriffsschicht

Das [Buch-Repository](https://github.com/msgoleli/fastapi/blob/buch/src/buch/repository/buch_repository.py) lädt Bücher
zusammen mit ihren Autoren und Verlagen und kapselt Hinzufügen und Löschen des
Buch-Aggregats. SQLAlchemy-Sessions werden über [session_factory.py](https://github.com/msgoleli/fastapi/blob/buch/src/buch/repository/session_factory.py)
verwaltet.
