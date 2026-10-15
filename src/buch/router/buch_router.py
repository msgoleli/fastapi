"""REST-Endpunkte für den Bücherkatalog."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from buch.entity import Autor, Buch, Verlag
from buch.repository import Session
from buch.repository.buch_repository import BuchRepository
from buch.security import Role, RolesRequired

router = APIRouter(prefix="/buecher", tags=["Bücher"])
repository = BuchRepository()


class BuchInput(BaseModel):
    titel: str = Field(min_length=1, max_length=300)
    isbn: str = Field(pattern=r"^(?:\d{10}|\d{13})$")
    erscheinungsdatum: date
    genre: str = Field(min_length=1, max_length=100)
    verlag_id: int
    autoren_ids: list[int] = []


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


def from_input(data: BuchInput, session) -> Buch:
    publisher = session.get(Verlag, data.verlag_id)
    if publisher is None:
        raise HTTPException(status_code=404, detail="Verlag nicht gefunden")
    authors = list(session.scalars(select(Autor).where(Autor.id.in_(data.autoren_ids))))
    if len(authors) != len(set(data.autoren_ids)):
        raise HTTPException(status_code=404, detail="Autor nicht gefunden")
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
        return output(repository.get(session, book.id))


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
        replacement = from_input(data, session)
        book.titel = replacement.titel
        book.isbn = replacement.isbn
        book.erscheinungsdatum = replacement.erscheinungsdatum
        book.genre = replacement.genre
        book.verlag = replacement.verlag
        book.verlag_id = replacement.verlag_id
        book.autoren = replacement.autoren
        session.flush()
        return output(repository.get(session, buch_id))


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
