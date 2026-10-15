"""Tests des Buch-Aggregats mit einer isolierten SQLite-Datenbank."""

from datetime import date
from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session as OrmSession, selectinload, sessionmaker

from buch.entity import Autor, Base, Buch, Verlag


@pytest.fixture
def db_session() -> Iterator[OrmSession]:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as session:
        yield session
    engine.dispose()


def test_book_aggregate_keeps_author_and_publisher_as_references(
    db_session: OrmSession,
) -> None:
    publisher = Verlag(name="Nordlicht", sitz="Hamburg", website="https://example.org")
    author = Autor(vorname="Mira", nachname="Beispiel", email="mira@example.org")
    db_session.add_all([publisher, author])
    db_session.flush()

    book = Buch(
        titel="Der Katalog",
        isbn="9781234567897",
        erscheinungsdatum=date(2024, 3, 15),
        genre="Roman",
        verlag_id=publisher.id,
        verlag=publisher,
        autoren=[author],
    )
    db_session.add(book)
    db_session.commit()

    loaded = db_session.scalar(
        select(Buch)
        .options(selectinload(Buch.autoren), selectinload(Buch.verlag))
        .where(Buch.id == book.id)
    )
    assert loaded is not None
    assert [item.email for item in loaded.autoren] == ["mira@example.org"]
    assert loaded.verlag.name == "Nordlicht"

    db_session.delete(loaded)
    db_session.commit()
    assert db_session.get(Autor, author.id) is not None
    assert db_session.get(Verlag, publisher.id) is not None
