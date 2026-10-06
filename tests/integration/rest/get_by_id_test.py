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

"""Tests für GET mit Pfadparameter für die ID."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, login, rest_url, timeout
from requests import get


# in pyproject.toml bei der Table [tool.pytest.ini_options] gibt es das Array "markers"
@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("patient_id", [30, 1, 20])
def test_get_by_id_admin(patient_id: int) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{patient_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    id_actual: Final = response_body.get("id")
    assert id_actual is not None
    assert id_actual == patient_id


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("patient_id", [0, 999999])
def test_get_by_id_not_found(patient_id: int) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{patient_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.rest
@pytest.mark.get_request
def test_get_by_id_patient() -> None:
    # arrange
    patient_id: Final = 20
    token: Final = login(username="alice")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{patient_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    patient_id_response: Final = response_body.get("id")
    assert patient_id_response is not None
    assert patient_id_response == patient_id


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("patient_id", [1, 30])
def test_get_by_id_not_allowed(patient_id: int) -> None:
    # arrange
    token: Final = login(username="alice")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{patient_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("patient_id", [0, 999999])
def test_get_by_id_not_allowed_not_found(patient_id: int) -> None:
    # arrange
    token: Final = login(username="alice")
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/{patient_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("patient_id", [30, 1, 20])
def test_get_by_id_ungueltiger_token(patient_id: int) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}XXX"}

    # act
    response: Final = get(
        f"{rest_url}/{patient_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("patient_id", [30, 1, 20])
def test_get_by_id_ohne_token(patient_id: int) -> None:
    # act
    response: Final = get(
        f"{rest_url}/{patient_id}",
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize(("patient_id", "if_none_match"), [(20, '"0"'), (30, '"0"')])
def test_get_by_id_etag(patient_id: int, if_none_match: str) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-None-Match": if_none_match,
    }

    # act
    response: Final = get(
        f"{rest_url}/{patient_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_MODIFIED
    assert not response.text


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize(
    ("patient_id", "if_none_match"),
    [(30, 'xxx"'), (1, "xxx"), (20, "xxx")],
)
def test_get_by_id_etag_invalid(patient_id: int, if_none_match: str) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-None-Match": if_none_match,
    }

    # act
    response: Final = get(
        f"{rest_url}/{patient_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    id_actual: Final = response_body.get("id")
    assert id_actual is not None
    assert id_actual == patient_id
