"""Pflege der eigenständigen Autoren- und Verlagsreferenzen."""

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, select

from buch.entity import Autor, Buch, Verlag
from buch.repository import Session
from buch.security import Role, RolesRequired
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(tags=["Autoren und Verlage"])


class AutorInput(BaseModel):
    vorname: str = Field(min_length=1, max_length=120)
    nachname: str = Field(min_length=1, max_length=120)
    email: EmailStr


class VerlagInput(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    sitz: str = Field(min_length=1, max_length=200)
    website: str | None = None


@router.get("/autoren")
def list_authors() -> list[dict[str, object]]:
    with Session() as session:
        return [
            {"id": a.id, "vorname": a.vorname, "nachname": a.nachname, "email": a.email}
            for a in session.scalars(
                select(Autor).order_by(Autor.nachname, Autor.vorname)
            )
        ]


@router.post(
    "/autoren",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def create_author(data: AutorInput) -> dict[str, object]:
    with Session.begin() as session:
        author = Autor(**data.model_dump())
        session.add(author)
        session.flush()
        return {"id": author.id, **data.model_dump()}


@router.get("/verlage")
def list_publishers() -> list[dict[str, object]]:
    with Session() as session:
        return [
            {"id": p.id, "name": p.name, "sitz": p.sitz, "website": p.website}
            for p in session.scalars(select(Verlag).order_by(Verlag.name))
        ]


@router.post(
    "/verlage",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def create_publisher(data: VerlagInput) -> dict[str, object]:
    with Session.begin() as session:
        publisher = Verlag(**data.model_dump())
        session.add(publisher)
        session.flush()
        return {"id": publisher.id, **data.model_dump()}


@router.get("/autoren/{autor_id}")
def get_author(autor_id: int) -> dict[str, object]:
    with Session() as session:
        author = session.get(Autor, autor_id)
        if author is None:
            raise HTTPException(status_code=404, detail="Autor nicht gefunden")
        return {
            "id": author.id,
            "vorname": author.vorname,
            "nachname": author.nachname,
            "email": author.email,
        }


@router.get("/verlage/{verlag_id}")
def get_publisher(verlag_id: int) -> dict[str, object]:
    with Session() as session:
        publisher = session.get(Verlag, verlag_id)
        if publisher is None:
            raise HTTPException(status_code=404, detail="Verlag nicht gefunden")
        return {
            "id": publisher.id,
            "name": publisher.name,
            "sitz": publisher.sitz,
            "website": publisher.website,
        }


@router.put(
    "/autoren/{autor_id}",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def update_author(autor_id: int, data: AutorInput) -> dict[str, object]:
    with Session.begin() as session:
        author = session.get(Autor, autor_id)
        if author is None:
            raise HTTPException(status_code=404, detail="Autor nicht gefunden")
        author.vorname = data.vorname
        author.nachname = data.nachname
        author.email = data.email
        return {"id": autor_id, **data.model_dump()}


@router.delete(
    "/autoren/{autor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def delete_author(autor_id: int) -> None:
    with Session.begin() as session:
        author = session.get(Autor, autor_id)
        if author is None:
            raise HTTPException(status_code=404, detail="Autor nicht gefunden")
        if author.buecher:
            raise HTTPException(
                status_code=409, detail="Autor ist noch Büchern zugeordnet"
            )
        session.delete(author)


@router.put(
    "/verlage/{verlag_id}",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def update_publisher(verlag_id: int, data: VerlagInput) -> dict[str, object]:
    with Session.begin() as session:
        publisher = session.get(Verlag, verlag_id)
        if publisher is None:
            raise HTTPException(status_code=404, detail="Verlag nicht gefunden")
        publisher.name = data.name
        publisher.sitz = data.sitz
        publisher.website = data.website
        return {"id": verlag_id, **data.model_dump()}


@router.delete(
    "/verlage/{verlag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
def delete_publisher(verlag_id: int) -> None:
    with Session.begin() as session:
        publisher = session.get(Verlag, verlag_id)
        if publisher is None:
            raise HTTPException(status_code=404, detail="Verlag nicht gefunden")
        book_count = session.scalar(
            select(func.count()).select_from(Buch).where(Buch.verlag_id == verlag_id)
        )
        if book_count:
            raise HTTPException(
                status_code=409, detail="Verlag veröffentlicht noch Bücher"
            )
        session.delete(publisher)
