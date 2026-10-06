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

"""Tests für Login."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import (
    base_url,
    certificate_path,
    login,
    timeout,
    token_path,
    username_admin,
)
from requests import request


@pytest.mark.login
def test_login_admin() -> None:
    # act
    token: Final = login()

    # then
    assert isinstance(token, str)
    assert token


@pytest.mark.login
def test_login_falsches_passwort() -> None:
    # arrange
    login_data: Final = {"username": username_admin, "password": "FALSCHES_PASSWORT"}

    # act
    response: Final = request(
        method="QUERY",
        url=f"{base_url}{token_path}",
        json=login_data,
        timeout=timeout,
        verify=certificate_path,
    )

    # then
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.login
def test_login_ohne_daten() -> None:
    # arrange
    login_data: dict[str, str] = {}

    # act
    response: Final = request(
        method="QUERY",
        url=f"{base_url}{token_path}",
        json=login_data,
        timeout=timeout,
        verify=certificate_path,
    )

    # then
    assert response.status_code == HTTPStatus.UNAUTHORIZED
