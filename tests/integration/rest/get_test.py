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

"""Tests für GET mit Query-Parameter."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, login, rest_url, timeout
from requests import get


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("email", ["admin@acme.com", "alice@acme.edu", "alice@acme.de"])
def test_get_by_email(email: str) -> None:
    # arrange
    params = {"email": email}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        rest_url,
        params=params,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    content: Final = response_body["content"]
    assert isinstance(content, list)
    assert len(content) == 1
    patient = content[0]
    assert patient is not None
    assert patient.get("email") == email
    assert patient.get("id") is not None


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("email", ["nicht@vorhanden.com", "joe.doe@acme.de"])
def test_get_by_email_not_found(email: str) -> None:
    # arrange
    params = {"email": email}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        rest_url,
        params=params,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("teil", ["Alice", "n"])
def test_get_by_nachname(teil: str) -> None:
    # arrange
    params = {"nachname": teil}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        rest_url,
        params=params,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    response_body: Final = response.json()
    assert isinstance(response_body, dict)
    content: Final = response_body["content"]
    for p in content:
        nachname = p.get("nachname")
        assert nachname is not None
        assert isinstance(nachname, str)
        assert teil.lower() in nachname.lower()
        assert p.get("id") is not None


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("nachname", ["Notfound", "Foo-Bar"])
def test_get_by_nachname_not_found(nachname: str) -> None:
    # arrange
    params = {"nachname": nachname}
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        rest_url,
        params=params,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("teil", ["a", "n"])
def test_get_nachnamen(teil: str) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/nachnamen/{teil}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.OK
    nachnamen: Final = response.json()
    assert isinstance(nachnamen, list)
    assert len(nachnamen) > 0
    for nachname in nachnamen:
        assert teil in nachname.lower()


@pytest.mark.rest
@pytest.mark.get_request
@pytest.mark.parametrize("teil", ["xxx", "Abc"])
def test_get_nachnamen_not_found(teil: str) -> None:
    # arrange
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = get(
        f"{rest_url}/nachnamen/{teil}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND
