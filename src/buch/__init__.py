"""Bücherkatalog-Anwendung und Paket-Einstiegspunkt."""

from buch.asgi_server import run
from buch.fastapi_app import app

__all__ = ["app", "main"]


def main() -> None:
    """Startet den konfigurierten Uvicorn-Server."""
    run()
