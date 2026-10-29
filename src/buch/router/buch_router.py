"""REST-Endpunkte für Bücher."""

from datetime import date
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError
from sqlalchemy import select
from sqlalchemy.orm import Session as OrmSession

from buch.entity import Autor, Buch, Verlag
from buch.repository import Session
from buch.repository.buch_repository import BuchRepository, BuchSuchkriterien
from buch.security import Role, RolesRequired
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/buecher", tags=["Bücher"])
query_router = APIRouter(tags=["Bücher"])
repository = BuchRepository()


class BuchInput(BaseModel):
    titel: str = Field(min_length=1, max_length=300)
    isbn: str = Field(pattern=r"^(?:\d{10}|\d{13})$")
    erscheinungsdatum: date
    genre: str = Field(min_length=1, max_length=100)
    verlag_id: int = Field(gt=0)
    autoren_ids: list[int] = Field(default_factory=list)


class BuchOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titel: str
    isbn: str
    erscheinungsdatum: date
    genre: str
    verlag_id: int
    verlag: str
    autoren: list[str]


class BuchSuchparameter(BaseModel):
    """Suchkriterien, die der QUERY-Request als JSON-Body übermittelt."""

    titel: str | None = Field(default=None, min_length=1, max_length=300)
    isbn: str | None = Field(default=None, pattern=r"^(?:\d{10}|\d{13})$")
    genre: str | None = Field(default=None, min_length=1, max_length=100)
    verlag_id: int | None = Field(default=None, gt=0)
    autor_id: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def require_search_criteria(self) -> Self:
        if all(
            value is None
            for value in (
                self.titel,
                self.isbn,
                self.genre,
                self.verlag_id,
                self.autor_id,
            )
        ):
            raise PydanticCustomError(
                "missing_search_criteria",
                "Mindestens ein Suchkriterium muss angegeben werden.",
            )
        return self


def output(book: Buch) -> BuchOutput:
    return BuchOutput(
        id=book.id,
        titel=book.titel,
        isbn=book.isbn,
        erscheinungsdatum=book.erscheinungsdatum,
        genre=book.genre,
        verlag_id=book.verlag_id,
        verlag=book.verlag.name,
        autoren=[f"{author.vorname} {author.nachname}" for author in book.autoren],
    )


@query_router.api_route(
    path="/query",
    methods=["QUERY"],
    response_model=list[BuchOutput],
)
def query_books(search: BuchSuchparameter) -> list[BuchOutput]:
    """Sucht Bücher mit HTTP QUERY und Kriterien aus dem JSON-Request-Body."""
    with Session() as session:
        return [
            output(book)
            for book in repository.find(
                session,
                BuchSuchkriterien(**search.model_dump(exclude_none=True)),
            )
        ]


def references_from_input(
    data: BuchInput,
    session: OrmSession,
) -> tuple[Verlag, list[Autor]]:
    publisher = session.get(Verlag, data.verlag_id)
    if publisher is None:
        raise HTTPException(status_code=404, detail="Verlag nicht gefunden")
    authors = list(session.scalars(select(Autor).where(Autor.id.in_(data.autoren_ids))))
    if len(authors) != len(set(data.autoren_ids)):
        raise HTTPException(status_code=404, detail="Autor nicht gefunden")
    return publisher, authors


def from_input(data: BuchInput, session: OrmSession) -> Buch:
    publisher, authors = references_from_input(data, session)
    return Buch(
        titel=data.titel,
        isbn=data.isbn,
        erscheinungsdatum=data.erscheinungsdatum,
        genre=data.genre,
        verlag_id=publisher.id,
        verlag=publisher,
        autoren=authors,
    )


@router.get("", response_model=list[BuchOutput])
def list_books(q: str | None = None) -> list[BuchOutput]:
    with Session() as session:
        return [output(book) for book in repository.list(session, q)]


@router.get("/{buch_id}", response_model=BuchOutput)
def get_book(buch_id: int) -> BuchOutput:
    with Session() as session:
        book = repository.get(session, buch_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Buch nicht gefunden")
        return output(book)


@router.post(
    "",
    response_model=BuchOutput,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def create_book(data: BuchInput) -> BuchOutput:
    with Session.begin() as session:
        book = repository.add(session, from_input(data, session))
        session.flush()
        session.refresh(book)
        created = repository.get(session, book.id)
        if created is None:
            raise HTTPException(
                status_code=500, detail="Buch konnte nicht geladen werden"
            )
        return output(created)


@router.put(
    "/{buch_id}",
    response_model=BuchOutput,
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def update_book(buch_id: int, data: BuchInput) -> BuchOutput:
    with Session.begin() as session:
        book = repository.get(session, buch_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Buch nicht gefunden")
        publisher, authors = references_from_input(data, session)
        book.titel = data.titel
        book.isbn = data.isbn
        book.erscheinungsdatum = data.erscheinungsdatum
        book.genre = data.genre
        book.verlag = publisher
        book.verlag_id = publisher.id
        book.autoren = authors
        session.flush()
        updated = repository.get(session, buch_id)
        if updated is None:
            raise HTTPException(
                status_code=500, detail="Buch konnte nicht geladen werden"
            )
        return output(updated)


@router.delete(
    "/{buch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def delete_book(buch_id: int) -> None:
    with Session.begin() as session:
        book = repository.get(session, buch_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Buch nicht gefunden")
        repository.delete(session, book)
