"""Fixtures für Unit-Tests des Bücherkatalogs."""

import pytest
from pytest_mock import MockerFixture

from buch.repository.buch_repository import BuchRepository


@pytest.fixture
def buch_repository() -> BuchRepository:
    """Stellt ein Repository ohne Datenbankverbindung bereit."""
    return BuchRepository()


@pytest.fixture
def session_mock(mocker: MockerFixture):
    """Stellt eine Mock-Session für isolierte Repository-Tests bereit."""
    return mocker.MagicMock()
