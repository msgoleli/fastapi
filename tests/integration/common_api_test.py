# Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Allgemeine Daten für die Integrationstests."""

from http import HTTPStatus
from pathlib import Path
from typing import Any, Final

from requests import get, post, request

__all__ = [
    "base_url",
    "certificate_path",
    "db_populate",
    "db_populate_path",
    "graphql_path",
    "graphql_url",
    "health_url",
    "keycloak_populate",
    "keycloak_populate_path",
    "login",
    "login_graphql",
    "password_admin",
    "rest_path",
    "rest_url",
    "timeout",
    "token_path",
    "username_admin",
]

schema: Final = "https"
port: Final = 8000
# TODO bei Windows: "localhost"
host: Final = "127.0.0.1"
base_url: Final = f"{schema}://{host}:{port}"
rest_path: Final = "/rest"
rest_url: Final = f"{base_url}{rest_path}"
health_url: Final = f"{base_url}/health"
graphql_path: Final = "/graphql"
graphql_url: Final = f"{base_url}/graphql"
token_path: Final = "/auth/token"  # ruff: ignore[hardcoded-password-string]
db_populate_path: Final = "/dev/db_populate"
keycloak_populate_path: Final = "/dev/keycloak_populate"
username_admin: Final = "admin"
password_admin: Final = "p"  # ruff: ignore[hardcoded-password-string]  # NOSONAR
timeout: Final = 2
# timeout: Final = 5
certificate_path: Final = str(Path("tests") / "integration" / "certificate.crt")


def check_readiness() -> None:
    response: Final = get(
        f"{health_url}/readiness",
        timeout=timeout,
        verify=certificate_path,
    )
    if response.status_code != HTTPStatus.OK:
        raise RuntimeError(f"readiness mit Statuscode {response.status_code}")
    response_body: Final = response.json()
    if not isinstance(response_body, dict):
        raise TypeError("readiness ohne Dictionary im Response-Body")
    status: Final[Any | None] = response_body.get("db")
    if status != "up":
        raise RuntimeError(f"readiness mit Meldungstext {status}")


def login(
    username: str = username_admin,
    password: str = password_admin,  # NOSONAR
) -> str:
    """Login an der REST-Schnittstelle, um einen Token von Keycloak zu erhalten."""
    login_data: Final = {"username": username, "password": password}
    response: Final = request(
        method="QUERY",
        url=f"{base_url}{token_path}",
        json=login_data,
        timeout=timeout,
        verify=certificate_path,
    )
    if response.status_code != HTTPStatus.OK:
        raise RuntimeError(f"login() mit Statuscode {response.status_code}")
    response_body: Final = response.json()
    token: Final = response_body.get("token")
    if token is None or not isinstance(token, str):
        raise RuntimeError(f"login() mit ungueltigem Token: type={type(token)}")
    return token


def login_graphql(
    username: str = username_admin,
    password: str = password_admin,  # NOSONAR
) -> str:
    """Login an der GraphQL-Schnittstelle, um einen Token von Keycloakzu erhalten."""
    login_query: Final = {
        "query": f'mutation {{ login(username: "{username}", password: "{password}") {{ token }} }}',  # ruff: ignore[line-too-long]
    }
    response: Final = post(
        f"{base_url}{graphql_path}",
        json=login_query,
        timeout=timeout,
        verify=certificate_path,
    )
    if response.status_code != HTTPStatus.OK:
        raise RuntimeError(f"login() mit Statuscode {response.status_code}")
    response_body: Final = response.json()
    token: Final = response_body.get("data").get("login").get("token")
    if token is None or not isinstance(token, str):
        raise RuntimeError(f"login_query() mit ungueltigem Token: type={type(token)}")
    return token


def db_populate() -> None:
    """Neuladen der DB."""
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}
    # Request('POST', url, data=data, headers=headers)
    response: Final = request(
        method="QUERY",
        url=f"{base_url}{db_populate_path}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )
    assert response.status_code == HTTPStatus.OK


def keycloak_populate() -> None:
    """Neuladen von Keycloak."""
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}
    response: Final = request(
        method="QUERY",
        url=f"{base_url}{keycloak_populate_path}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )
    assert response.status_code == HTTPStatus.OK
