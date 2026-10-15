"""Autorinnen und Autoren, die mehreren Büchern zugeordnet sein können."""

from typing import override

from sqlalchemy import Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from buch.entity.base import Base
from buch.entity.buch import buch_autor


class Autor(Base):
    """Person, die ein oder mehrere Bücher verfasst."""

    __tablename__ = "autor"

    vorname: Mapped[str]
    nachname: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    id: Mapped[int] = mapped_column(Identity(), primary_key=True, init=False)
    buecher: Mapped[list["Buch"]] = relationship(
        secondary=buch_autor,
        back_populates="autoren",
        default_factory=list,
    )

    @override
    def __repr__(self) -> str:
        return f"Autor(id={self.id}, name={self.vorname} {self.nachname})"
