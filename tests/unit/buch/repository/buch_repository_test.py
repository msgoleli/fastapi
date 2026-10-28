"""Unit-Tests des Buch-Repositories ohne echte Datenbank."""

from datetime import date

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session

from buch.entity import Buch, Verlag
from buch.repository.buch_repository import BuchRepository


@pytest.fixture
def buch() -> Buch:
    """Baut ein Buch mit Verlag als Repository-Testdaten."""
    verlag = Verlag(name="Nordlicht", sitz="Hamburg")
    return Buch(
        titel="Der Katalog",
        isbn="9781234567897",
        erscheinungsdatum=date(2024, 3, 15),
        genre="Roman",
        verlag_id=1,
        verlag=verlag,
        autoren=[],
    )


@pytest.mark.unit
def test_get_returns_book_from_session(
    buch_repository: BuchRepository,
    session_mock: Session,
    buch: Buch,
) -> None:
    session_mock.scalar.return_value = buch  # ty: ignore[unresolved-attribute]

    result = buch_repository.get(session_mock, 1)

    assert result is buch
    session_mock.scalar.assert_called_once()  # ty: ignore[unresolved-attribute]


@pytest.mark.unit
def test_get_returns_none_when_book_does_not_exist(
    buch_repository: BuchRepository,
    session_mock: Session,
) -> None:
    session_mock.scalar.return_value = None  # ty: ignore[unresolved-attribute]

    result = buch_repository.get(session_mock, 404)

    assert result is None
    session_mock.scalar.assert_called_once()  # ty: ignore[unresolved-attribute]


@pytest.mark.unit
def test_list_returns_unique_books_matching_title(
    buch_repository: BuchRepository,
    session_mock: Session,
    buch: Buch,
    mocker: MockerFixture,
) -> None:
    scalar_result = mocker.MagicMock()
    scalar_result.unique.return_value = [buch]
    session_mock.scalars.return_value = scalar_result  # ty: ignore[unresolved-attribute]

    result = buch_repository.list(session_mock, "Katalog")

    assert result == [buch]
    session_mock.scalars.assert_called_once()  # ty: ignore[unresolved-attribute]
    scalar_result.unique.assert_called_once_with()


@pytest.mark.unit
def test_add_stores_and_flushes_book(
    buch_repository: BuchRepository,
    session_mock: Session,
    buch: Buch,
) -> None:
    result = buch_repository.add(session_mock, buch)

    assert result is buch
    session_mock.add.assert_called_once_with(buch)  # ty: ignore[unresolved-attribute]
    session_mock.flush.assert_called_once_with()  # ty: ignore[unresolved-attribute]


@pytest.mark.unit
def test_delete_removes_book_from_session(
    buch_repository: BuchRepository,
    session_mock: Session,
    buch: Buch,
) -> None:
    buch_repository.delete(session_mock, buch)

    session_mock.delete.assert_called_once_with(buch)  # ty: ignore[unresolved-attribute]
