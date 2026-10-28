"""GraphQL-Schema für Bücher, Autoren und Verlage."""

from typing import Final

import strawberry
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from buch.entity import Autor, Buch, Verlag
from buch.graphql_api.graphql_types import AutorType, BuchInput, BuchType, VerlagType
from buch.repository import Session
from buch.security import Role, TokenService


def author_type(author: Autor) -> AutorType:
    return AutorType(
        id=author.id,
        vorname=author.vorname,
        nachname=author.nachname,
        email=author.email,
    )


def publisher_type(publisher: Verlag) -> VerlagType:
    return VerlagType(
        id=publisher.id,
        name=publisher.name,
        sitz=publisher.sitz,
        website=publisher.website,
    )


def book_type(book: Buch) -> BuchType:
    return BuchType(
        id=book.id,
        titel=book.titel,
        isbn=book.isbn,
        erscheinungsdatum=book.erscheinungsdatum,
        genre=book.genre,
        verlag=publisher_type(book.verlag),
        autoren=[author_type(author) for author in book.autoren],
    )


@strawberry.type
class Query:
    @strawberry.field
    def buecher(self, titel: str | None = None) -> list[BuchType]:
        with Session() as session:
            statement = select(Buch).options(
                selectinload(Buch.verlag), selectinload(Buch.autoren)
            )
            if titel:
                statement = statement.where(Buch.titel.ilike(f"%{titel}%"))
            return [book_type(book) for book in session.scalars(statement).unique()]

    @strawberry.field
    def buch(self, id: int) -> BuchType | None:  # ruff: ignore[builtin-argument-shadowing]
        with Session() as session:
            book = session.scalar(
                select(Buch)
                .options(selectinload(Buch.verlag), selectinload(Buch.autoren))
                .where(Buch.id == id)
            )
            return book_type(book) if book else None

    @strawberry.field
    def autoren(self) -> list[AutorType]:
        with Session() as session:
            return [
                author_type(a)
                for a in session.scalars(select(Autor).order_by(Autor.nachname))
            ]

    @strawberry.field
    def verlage(self) -> list[VerlagType]:
        with Session() as session:
            return [
                publisher_type(p)
                for p in session.scalars(select(Verlag).order_by(Verlag.name))
            ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def buch_anlegen(self, buch: BuchInput, info: Info) -> BuchType:
        request = info.context.get("request")
        user = TokenService().get_user_from_request(request)
        if Role.ADMIN not in user.roles:
            raise PermissionError("Für diese Aktion ist die ADMIN-Rolle erforderlich.")  # ruff: ignore[raise-vanilla-args]
        with Session.begin() as session:
            publisher = session.get(Verlag, buch.verlag_id)
            authors = list(
                session.scalars(select(Autor).where(Autor.id.in_(buch.autoren_ids)))
            )
            if publisher is None or len(authors) != len(set(buch.autoren_ids)):
                raise ValueError("Verlag oder Autor nicht gefunden")  # ruff: ignore[raise-vanilla-args]
            book = Buch(
                titel=buch.titel,
                isbn=buch.isbn,
                erscheinungsdatum=buch.erscheinungsdatum,
                genre=buch.genre,
                verlag_id=publisher.id,
                verlag=publisher,
                autoren=authors,
            )
            session.add(book)
            session.flush()
            session.refresh(book)
            return book_type(book)


schema: Final = strawberry.Schema(query=Query, mutation=Mutation)
graphql_router: Final = GraphQLRouter(schema)
