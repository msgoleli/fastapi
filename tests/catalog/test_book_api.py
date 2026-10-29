"""API-Integrationstests mit einer isolierten SQLite-Datenbank."""

from collections.abc import Iterator, Mapping
from http import HTTPStatus
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
        TestTokenService,
    )

    Base.metadata.create_all(engine)
    with TestClient(app) as test_client:
        yield test_client
    engine.dispose()


def create_references(client: TestClient, suffix: str = "") -> tuple[int, int]:
    """Legt Testautor und Testverlag an und liefert ihre IDs zurück."""
    headers = {"Authorization": "Bearer test-admin"}
    author_response = client.post(
        "/rest/autoren",
        headers=headers,
        json={
            "vorname": "Mira",
            "nachname": f"Beispiel{suffix}",
            "email": f"mira{suffix or '-default'}@example.org",
        },
    )
    publisher_response = client.post(
        "/rest/verlage",
        headers=headers,
        json={
            "name": f"Nordlicht{suffix}",
            "sitz": "Hamburg",
            "website": "https://example.org",
        },
    )
    assert author_response.status_code == HTTPStatus.CREATED
    assert publisher_response.status_code == HTTPStatus.CREATED
    return author_response.json()["id"], publisher_response.json()["id"]


def create_book(client: TestClient, book: Mapping[str, object]) -> dict[str, object]:
    """Legt ein Buch für API-Tests an und liefert die Antwort zurück."""
    response = client.post(
        "/rest/buecher",
        headers={"Authorization": "Bearer test-admin"},
        json=book,
    )
    assert response.status_code == HTTPStatus.CREATED
    return response.json()


def test_write_endpoints_require_an_admin_token(client: TestClient) -> None:
    response = client.post(
        "/rest/verlage",
        json={"name": "Nordlicht", "sitz": "Hamburg", "website": None},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED


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

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["verlag"] == "Nordlicht"
    assert response.json()["autoren"] == ["Mira Beispiel"]

    listing = client.get("/rest/buecher", params={"q": "Katalog"})
    assert listing.status_code == HTTPStatus.OK
    assert [book["titel"] for book in listing.json()] == ["Der Katalog"]


@pytest.mark.query_request
@pytest.mark.parametrize(
    ("criteria", "expected_title"),
    [
        ({"titel": "KATALOG"}, "Der Katalog"),
        ({"isbn": "9781234567897"}, "Der Katalog"),
        ({"genre": "rOm"}, "Der Katalog"),
    ],
)
def test_query_method_searches_books_from_json_body(
    client: TestClient,
    criteria: dict[str, str],
    expected_title: str,
) -> None:
    author_id, publisher_id = create_references(client)
    create_book(
        client,
        {
            "titel": "Der Katalog",
            "isbn": "9781234567897",
            "erscheinungsdatum": "2024-03-15",
            "genre": "Roman",
            "verlag_id": publisher_id,
            "autoren_ids": [author_id],
        },
    )
    create_book(
        client,
        {
            "titel": "GraphQL Kompendium",
            "isbn": "9781234567804",
            "erscheinungsdatum": "2024-03-15",
            "genre": "Sachbuch",
            "verlag_id": publisher_id,
            "autoren_ids": [author_id],
        },
    )

    response = client.request("QUERY", "/rest/query", json=criteria)

    assert response.status_code == HTTPStatus.OK
    assert [book["titel"] for book in response.json()] == [expected_title]


@pytest.mark.query_request
def test_query_method_combines_book_publisher_and_author_filters(
    client: TestClient,
) -> None:
    author_id, publisher_id = create_references(client)
    other_author_id, other_publisher_id = create_references(client, suffix="-zweit")
    create_book(
        client,
        {
            "titel": "Der Katalog",
            "isbn": "9781234567897",
            "erscheinungsdatum": "2024-03-15",
            "genre": "Roman",
            "verlag_id": publisher_id,
            "autoren_ids": [author_id],
        },
    )
    create_book(
        client,
        {
            "titel": "Der Katalog: zweite Ausgabe",
            "isbn": "9781234567804",
            "erscheinungsdatum": "2024-03-15",
            "genre": "Roman",
            "verlag_id": other_publisher_id,
            "autoren_ids": [other_author_id],
        },
    )

    response = client.request(
        "QUERY",
        "/rest/query",
        json={
            "titel": "Katalog",
            "genre": "Roman",
            "verlag_id": publisher_id,
            "autor_id": author_id,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert [book["titel"] for book in response.json()] == ["Der Katalog"]


@pytest.mark.query_request
def test_query_method_returns_empty_list_when_nothing_matches(
    client: TestClient,
) -> None:
    response = client.request("QUERY", "/rest/query", json={"isbn": "0000000000"})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


@pytest.mark.query_request
@pytest.mark.parametrize(
    "criteria",
    [{}, {"titel": ""}, {"isbn": "123"}, {"verlag_id": 0}, {"autor_id": -1}],
)
def test_query_method_rejects_invalid_search_criteria(
    client: TestClient,
    criteria: dict[str, object],
) -> None:
    response = client.request("QUERY", "/rest/query", json=criteria)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.query_request
def test_query_method_rejects_malformed_json(client: TestClient) -> None:
    response = client.request(
        "QUERY",
        "/rest/query",
        content="{invalid json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.query_request
def test_query_method_is_not_exposed_as_get(client: TestClient) -> None:
    response = client.get("/rest/query")

    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_author_endpoints_support_list_get_update_and_delete(
    client: TestClient,
) -> None:
    author_id, _ = create_references(client)
    headers = {"Authorization": "Bearer test-admin"}

    listing = client.get("/rest/autoren")
    author = client.get(f"/rest/autoren/{author_id}")
    assert listing.status_code == HTTPStatus.OK
    assert author.status_code == HTTPStatus.OK
    assert author.json()["email"] == "mira-default@example.org"

    updated = client.put(
        f"/rest/autoren/{author_id}",
        headers=headers,
        json={
            "vorname": "Mira",
            "nachname": "Aktualisiert",
            "email": "mira.updated@example.org",
        },
    )
    deleted = client.delete(f"/rest/autoren/{author_id}", headers=headers)

    assert updated.status_code == HTTPStatus.OK
    assert updated.json()["nachname"] == "Aktualisiert"
    assert deleted.status_code == HTTPStatus.NO_CONTENT
    assert client.get(f"/rest/autoren/{author_id}").status_code == HTTPStatus.NOT_FOUND


def test_publisher_endpoints_support_list_get_update_and_delete(
    client: TestClient,
) -> None:
    _, publisher_id = create_references(client)
    headers = {"Authorization": "Bearer test-admin"}

    listing = client.get("/rest/verlage")
    publisher = client.get(f"/rest/verlage/{publisher_id}")
    assert listing.status_code == HTTPStatus.OK
    assert publisher.status_code == HTTPStatus.OK
    assert publisher.json()["name"] == "Nordlicht"

    updated = client.put(
        f"/rest/verlage/{publisher_id}",
        headers=headers,
        json={"name": "Sternenverlag", "sitz": "Berlin", "website": None},
    )
    deleted = client.delete(f"/rest/verlage/{publisher_id}", headers=headers)

    assert updated.status_code == HTTPStatus.OK
    assert updated.json()["name"] == "Sternenverlag"
    assert deleted.status_code == HTTPStatus.NO_CONTENT
    assert (
        client.get(f"/rest/verlage/{publisher_id}").status_code == HTTPStatus.NOT_FOUND
    )


def test_duplicate_author_email_and_publisher_name_return_conflict(
    client: TestClient,
) -> None:
    create_references(client)
    headers = {"Authorization": "Bearer test-admin"}

    duplicate_author = client.post(
        "/rest/autoren",
        headers=headers,
        json={
            "vorname": "Andere",
            "nachname": "Person",
            "email": "mira-default@example.org",
        },
    )
    duplicate_publisher = client.post(
        "/rest/verlage",
        headers=headers,
        json={"name": "Nordlicht", "sitz": "Kiel", "website": None},
    )

    assert duplicate_author.status_code == HTTPStatus.CONFLICT
    assert duplicate_publisher.status_code == HTTPStatus.CONFLICT


def test_referenced_author_and_publisher_cannot_be_deleted(client: TestClient) -> None:
    author_id, publisher_id = create_references(client)
    create_book(
        client,
        {
            "titel": "Der Katalog",
            "isbn": "9781234567897",
            "erscheinungsdatum": "2024-03-15",
            "genre": "Roman",
            "verlag_id": publisher_id,
            "autoren_ids": [author_id],
        },
    )
    headers = {"Authorization": "Bearer test-admin"}

    deleted_author = client.delete(f"/rest/autoren/{author_id}", headers=headers)
    deleted_publisher = client.delete(f"/rest/verlage/{publisher_id}", headers=headers)

    assert deleted_author.status_code == HTTPStatus.CONFLICT
    assert deleted_publisher.status_code == HTTPStatus.CONFLICT


def test_book_endpoints_support_get_update_and_delete(client: TestClient) -> None:
    author_id, publisher_id = create_references(client)
    created = create_book(
        client,
        {
            "titel": "Der Katalog",
            "isbn": "9781234567897",
            "erscheinungsdatum": "2024-03-15",
            "genre": "Roman",
            "verlag_id": publisher_id,
            "autoren_ids": [author_id],
        },
    )
    book_id = created["id"]
    headers = {"Authorization": "Bearer test-admin"}

    fetched = client.get(f"/rest/buecher/{book_id}")
    updated = client.put(
        f"/rest/buecher/{book_id}",
        headers=headers,
        json={
            "titel": "Der aktualisierte Katalog",
            "isbn": "9781234567804",
            "erscheinungsdatum": "2025-05-20",
            "genre": "Sachbuch",
            "verlag_id": publisher_id,
            "autoren_ids": [author_id],
        },
    )
    deleted = client.delete(f"/rest/buecher/{book_id}", headers=headers)

    assert fetched.status_code == HTTPStatus.OK
    assert fetched.json()["verlag"] == "Nordlicht"
    assert updated.status_code == HTTPStatus.OK
    assert updated.json()["titel"] == "Der aktualisierte Katalog"
    assert deleted.status_code == HTTPStatus.NO_CONTENT
    assert client.get(f"/rest/buecher/{book_id}").status_code == HTTPStatus.NOT_FOUND


def test_duplicate_book_isbn_returns_conflict(client: TestClient) -> None:
    author_id, publisher_id = create_references(client)
    payload = {
        "titel": "Der Katalog",
        "isbn": "9781234567897",
        "erscheinungsdatum": "2024-03-15",
        "genre": "Roman",
        "verlag_id": publisher_id,
        "autoren_ids": [author_id],
    }
    create_book(client, payload)

    response = client.post(
        "/rest/buecher",
        headers={"Authorization": "Bearer test-admin"},
        json=payload,
    )

    assert response.status_code == HTTPStatus.CONFLICT


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        ("GET", "/rest/buecher/999999", None),
        (
            "PUT",
            "/rest/buecher/999999",
            {
                "titel": "Nicht vorhanden",
                "isbn": "9781234567897",
                "erscheinungsdatum": "2024-03-15",
                "genre": "Roman",
                "verlag_id": 1,
                "autoren_ids": [],
            },
        ),
        ("DELETE", "/rest/buecher/999999", None),
    ],
)
def test_missing_book_get_update_and_delete_return_not_found(
    client: TestClient,
    method: str,
    path: str,
    body: dict[str, object] | None,
) -> None:
    response = client.request(
        method,
        path,
        headers={"Authorization": "Bearer test-admin"},
        json=body,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("titel", ""),
        ("isbn", "not-an-isbn"),
        ("erscheinungsdatum", "gestern"),
        ("genre", ""),
        ("verlag_id", 0),
    ],
)
def test_create_book_validates_required_properties(
    client: TestClient,
    field: str,
    value: object,
) -> None:
    author_id, publisher_id = create_references(client)
    payload: dict[str, object] = {
        "titel": "Der Katalog",
        "isbn": "9781234567897",
        "erscheinungsdatum": "2024-03-15",
        "genre": "Roman",
        "verlag_id": publisher_id,
        "autoren_ids": [author_id],
    }
    payload[field] = value

    response = client.post(
        "/rest/buecher",
        headers={"Authorization": "Bearer test-admin"},
        json=payload,
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("missing_reference", ["verlag_id", "autoren_ids"])
def test_create_book_rejects_unknown_references(
    client: TestClient,
    missing_reference: str,
) -> None:
    _, publisher_id = create_references(client)
    payload: dict[str, object] = {
        "titel": "Der Katalog",
        "isbn": "9781234567897",
        "erscheinungsdatum": "2024-03-15",
        "genre": "Roman",
        "verlag_id": publisher_id,
        "autoren_ids": [],
    }
    payload[missing_reference] = 999999
    if missing_reference == "autoren_ids":
        payload[missing_reference] = [999999]

    response = client.post(
        "/rest/buecher",
        headers={"Authorization": "Bearer test-admin"},
        json=payload,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


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

    assert response.status_code == HTTPStatus.OK
    assert "errors" not in response.json()
    assert response.json()["data"]["buchAnlegen"]["titel"] == "GraphQL im Katalog"

    listing = client.post(
        "/graphql",
        json={"query": "{ buecher { titel verlag { name } autoren { nachname } } }"},
    )
    assert listing.status_code == HTTPStatus.OK
    assert listing.json()["data"]["buecher"][0]["verlag"]["name"] == "Nordlicht"
