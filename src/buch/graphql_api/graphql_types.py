"""GraphQL-Datentypen für Bücher."""

from datetime import date

import strawberry


@strawberry.type
class AutorType:
    id: int
    vorname: str
    nachname: str
    email: str


@strawberry.type
class VerlagType:
    id: int
    name: str
    sitz: str
    website: str | None


@strawberry.type
class BuchType:
    id: int
    titel: str
    isbn: str
    erscheinungsdatum: date
    genre: str
    verlag: VerlagType
    autoren: list[AutorType]


@strawberry.input
class BuchInput:
    titel: str
    isbn: str
    erscheinungsdatum: date
    genre: str
    verlag_id: int
    autoren_ids: list[int]
