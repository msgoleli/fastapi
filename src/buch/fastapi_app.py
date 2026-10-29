"""FastAPI-Anwendung für Bücher."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.exc import IntegrityError
from starlette.middleware.base import RequestResponseEndpoint

from buch.banner import banner
from buch.entity import Base  # registriert alle ORM-Modelle
from buch.graphql_api import graphql_router
from buch.repository import engine
from buch.router import buch_router, katalog_router, query_router
from buch.router.health_router import router as health_router
from buch.router.shutdown_router import router as shutdown_router
from buch.security import (
    AuthorizationError,
    LoginError,
    router as auth_router,
    set_response_headers,
)
from fastapi import FastAPI, Request, Response


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    Base.metadata.create_all(bind=engine)
    banner(app.routes)
    try:
        yield
    finally:
        engine.dispose()


app = FastAPI(
    title="Buch API",
    description="REST-API zur Verwaltung von Büchern, Autoren und Verlagen.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "QUERY", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
Instrumentator().instrument(app).expose(app)
app.include_router(buch_router, prefix="/rest")
app.include_router(katalog_router, prefix="/rest")
app.include_router(query_router, prefix="/rest")
app.include_router(graphql_router, prefix="/graphql")
app.include_router(auth_router, prefix="/auth")
app.include_router(health_router, prefix="/health")
app.include_router(shutdown_router, prefix="/admin")


@app.middleware("http")
async def security_headers(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    response = await call_next(request)
    set_response_headers(response)
    return response


@app.exception_handler(IntegrityError)
def integrity_error_handler(_request: Request, _exc: IntegrityError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "detail": (
                "Der Datensatz verletzt eine eindeutige oder referenzielle Bedingung."
            )
        },
    )


@app.exception_handler(LoginError)
def login_error_handler(_request: Request, _exc: LoginError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": "Anmeldung fehlgeschlagen"})


@app.exception_handler(AuthorizationError)
def authorization_error_handler(
    _request: Request, _exc: AuthorizationError
) -> JSONResponse:
    return JSONResponse(
        status_code=401, content={"detail": "Authentifizierung erforderlich"}
    )
