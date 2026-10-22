"""API-Integrationstests mit einer isolierten SQLite-Datenbank."""

from collections.abc import Iterator
from importlib import import_module

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from buch.entity import Base
from buch.fastapi_app import app
from buch.security import AuthorizationError, Role, User
from buch.security.dependencies import get_token_service
from fastapi import Request

fastapi_app_module = import_module("buch.fastapi_app")
graphql_schema = import_module("buch.graphql_api.schema")
book_router = import_module("buch.router.buch_router")
catalog_router = import_module("buch.router.katalog_router")


class TestTokenService:
    """Test-Tokenservice, der keine Verbindung zu Keycloak benötigt."""

    def get_user_from_request(self, request: Request) -> User:
        if request.headers.get("Authorization") != "Bearer test-admin":
            raise AuthorizationError
        return User(
            username="admin",
            email="admin@example.org",
            nachname="Admin",
            vorname="Test",
            roles=[Role.ADMIN],
        )


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """FastAPI-Client mit SQLite und einem Test-Admin für die Rollenprüfung."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autoflush=False)

    monkeypatch.setattr(fastapi_app_module, "engine", engine)
    monkeypatch.setattr(book_router, "Session", session_factory)
    monkeypatch.setattr(catalog_router, "Session", session_factory)
    monkeypatch.setattr(graphql_schema, "Session", session_factory)
    monkeypatch.setattr(graphql_schema, "TokenService", TestTokenService)
    monkeypatch.setitem(
        app.dependency_overrides,
        get_token_service,
        lambda: TestTokenService(),
    )

    Base.metadata.create_all(engine)
    with TestClient(app) as test_client:
        yield test_client
    engine.dispose()


def create_references(client: TestClient) -> tuple[int, int]:
    """Legt Testautor und Testverlag an und liefert ihre IDs zurück."""
    headers = {"Authorization": "Bearer test-admin"}
    author_response = client.post(
        "/rest/autoren",
        headers=headers,
        json={"vorname": "Mira", "nachname": "Beispiel", "email": "mira@example.org"},
    )
    publisher_response = client.post(
        "/rest/verlage",
        headers=headers,
        json={"name": "Nordlicht", "sitz": "Hamburg", "website": "https://example.org"},
    )
    assert author_response.status_code == 201
    assert publisher_response.status_code == 201
    return author_response.json()["id"], publisher_response.json()["id"]


def test_write_endpoints_require_an_admin_token(client: TestClient) -> None:
    response = client.post(
        "/rest/verlage",
        json={"name": "Nordlicht", "sitz": "Hamburg", "website": None},
    )

    assert response.status_code == 401


def test_rest_creates_and_filters_a_book_aggregate(client: TestClient) -> None:
    author_id, publisher_id = create_references(client)
    response = client.post(
        "/rest/buecher",
        headers={"Authorization": "Bearer test-admin"},
        json={
            "titel": "Der Katalog",
            "isbn": "9781234567897",
            "erscheinungsdatum": "2024-03-15",
            "genre": "Roman",
            "verlag_id": publisher_id,
            "autoren_ids": [author_id],
        },
    )

    assert response.status_code == 201
    assert response.json()["verlag"] == "Nordlicht"
    assert response.json()["autoren"] == ["Mira Beispiel"]

    listing = client.get("/rest/buecher", params={"q": "Katalog"})
    assert listing.status_code == 200
    assert [book["titel"] for book in listing.json()] == ["Der Katalog"]


def test_graphql_lists_books_and_creates_one_with_admin(client: TestClient) -> None:
    author_id, publisher_id = create_references(client)
    response = client.post(
        "/graphql",
        headers={"Authorization": "Bearer test-admin"},
        json={
            "query": f"""
                mutation {{
                  buchAnlegen(buch: {{
                    titel: "GraphQL im Katalog"
                    isbn: "9781234567804"
                    erscheinungsdatum: "2024-04-20"
                    genre: "Sachbuch"
                    verlagId: {publisher_id}
                    autorenIds: [{author_id}]
                  }}) {{ id titel }}
                }}
            """
        },
    )

    assert response.status_code == 200
    assert "errors" not in response.json()
    assert response.json()["data"]["buchAnlegen"]["titel"] == "GraphQL im Katalog"

    listing = client.post(
        "/graphql",
        json={"query": "{ buecher { titel verlag { name } autoren { nachname } } }"},
    )
    assert listing.status_code == 200
    assert listing.json()["data"]["buecher"][0]["verlag"]["name"] == "Nordlicht"
