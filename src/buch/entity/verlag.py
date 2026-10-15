"""Verlage als Referenzentitäten für Bücher."""

from typing import override

from sqlalchemy import Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from buch.entity.base import Base


class Verlag(Base):
    """Verlag, der Bücher veröffentlicht."""

    __tablename__ = "verlag"

    name: Mapped[str] = mapped_column(unique=True)
    sitz: Mapped[str]
    website: Mapped[str | None] = mapped_column(default=None)
    id: Mapped[int] = mapped_column(Identity(), primary_key=True, init=False)
    buecher: Mapped[list["Buch"]] = relationship(back_populates="verlag", init=False)

    @override
    def __repr__(self) -> str:
        return f"Verlag(id={self.id}, name={self.name!r})"


from buch.entity.buch import Buch  # noqa: E402
