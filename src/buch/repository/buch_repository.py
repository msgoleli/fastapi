"""Datenzugriff für Buch-Aggregate."""

import builtins

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from buch.entity import Buch


class BuchRepository:
    """Lädt und speichert Bücher mitsamt ihrer Autoren."""

    def get(self, session: Session, buch_id: int) -> Buch | None:
        return session.scalar(
            select(Buch)
            .options(selectinload(Buch.autoren), selectinload(Buch.verlag))
            .where(Buch.id == buch_id)
        )

    def list(self, session: Session, q: str | None = None) -> builtins.list[Buch]:
        statement = select(Buch).options(
            selectinload(Buch.autoren), selectinload(Buch.verlag)
        )
        if q:
            statement = statement.where(Buch.titel.ilike(f"%{q}%"))
        return list(session.scalars(statement.order_by(Buch.titel)).unique())

    def add(self, session: Session, buch: Buch) -> Buch:
        session.add(buch)
        session.flush()
        return buch

    def delete(self, session: Session, buch: Buch) -> None:
        session.delete(buch)
