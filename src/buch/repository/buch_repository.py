"""Datenzugriff für Buch-Aggregate."""

import builtins
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from buch.entity import Autor, Buch


@dataclass(frozen=True, slots=True)
class BuchSuchkriterien:
    """Optional criteria shared with the repository query."""

    titel: str | None = None
    isbn: str | None = None
    genre: str | None = None
    verlag_id: int | None = None
    autor_id: int | None = None


class BuchRepository:
    """Lädt und speichert Bücher mitsamt ihrer Autoren."""

    def get(self, session: Session, buch_id: int) -> Buch | None:
        return session.scalar(
            select(Buch)
            .options(selectinload(Buch.autoren), selectinload(Buch.verlag))
            .where(Buch.id == buch_id)
        )

    def list(self, session: Session, q: str | None = None) -> builtins.list[Buch]:
        return self.find(session, BuchSuchkriterien(titel=q or None))

    def find(
        self,
        session: Session,
        criteria: BuchSuchkriterien,
    ) -> builtins.list[Buch]:
        """Findet Bücher mit allen angegebenen Kriterien."""
        statement = select(Buch).options(
            selectinload(Buch.autoren), selectinload(Buch.verlag)
        )
        if criteria.titel is not None:
            statement = statement.where(Buch.titel.ilike(f"%{criteria.titel}%"))
        if criteria.isbn is not None:
            statement = statement.where(Buch.isbn == criteria.isbn)
        if criteria.genre is not None:
            statement = statement.where(Buch.genre.ilike(f"%{criteria.genre}%"))
        if criteria.verlag_id is not None:
            statement = statement.where(Buch.verlag_id == criteria.verlag_id)
        if criteria.autor_id is not None:
            statement = statement.where(Buch.autoren.any(Autor.id == criteria.autor_id))
        return list(session.scalars(statement.order_by(Buch.titel)).unique())

    def add(self, session: Session, buch: Buch) -> Buch:
        session.add(buch)
        session.flush()
        return buch

    def delete(self, session: Session, buch: Buch) -> None:
        session.delete(buch)
