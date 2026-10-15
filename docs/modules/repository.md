# Datenzugriffsschicht

Das [Buch-Repository](../../src/buch/repository/buch_repository.py) lädt Bücher
zusammen mit ihren Autoren und Verlagen und kapselt Hinzufügen und Löschen des
Buch-Aggregats. SQLAlchemy-Sessions werden über [session_factory.py](../../src/buch/repository/session_factory.py)
verwaltet.
