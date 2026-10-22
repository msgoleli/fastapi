"""Buch als Aggregate Root des Katalogs."""

from datetime import date
from typing import TYPE_CHECKING, override

from sqlalchemy import Column, ForeignKey, Identity, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from buch.entity.base import Base

if TYPE_CHECKING:
    from buch.entity.autor import Autor
    from buch.entity.verlag import Verlag

buch_autor = Table(
    "buch_autor",
    Base.metadata,
    Column("buch_id", ForeignKey("buch.id", ondelete="CASCADE"), primary_key=True),
    Column("autor_id", ForeignKey("autor.id", ondelete="CASCADE"), primary_key=True),
)


class Buch(Base):
    """Ein Buch aggregiert seine Metadaten und die Zuordnung seiner Autoren."""

    __tablename__ = "buch"

    titel: Mapped[str]
    isbn: Mapped[str] = mapped_column(unique=True)
    erscheinungsdatum: Mapped[date]
    genre: Mapped[str]
    verlag_id: Mapped[int] = mapped_column(ForeignKey("verlag.id"))
    verlag: Mapped["Verlag"] = relationship(back_populates="buecher")
    id: Mapped[int] = mapped_column(Identity(), primary_key=True, init=False)
    autoren: Mapped[list["Autor"]] = relationship(
        secondary=buch_autor,
        back_populates="buecher",
        default_factory=list,
    )

    @override
    def __repr__(self) -> str:
        return f"Buch(id={self.id}, titel={self.titel!r}, isbn={self.isbn!r})"
