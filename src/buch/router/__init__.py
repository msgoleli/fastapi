"""HTTP-Routen für Bücher, Autoren und Verlage."""

from buch.router.buch_router import query_router, router as buch_router
from buch.router.katalog_router import router as katalog_router

__all__ = ["buch_router", "katalog_router", "query_router"]
