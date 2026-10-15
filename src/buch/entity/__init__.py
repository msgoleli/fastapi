"""Persistente Entitäten des Bücherkatalogs."""

from buch.entity.base import Base
from buch.entity.buch import Buch
from buch.entity.autor import Autor
from buch.entity.verlag import Verlag

__all__ = ["Autor", "Base", "Buch", "Verlag"]
