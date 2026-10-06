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

"""Tests für PUT."""

from http import HTTPStatus
from typing import Final

import pytest
from common_api_test import certificate_path, login, rest_url, timeout
from requests import put

EMAIL_UPDATE: Final = "alice@acme.de.put"
HOMEPAGE_UPDATE: Final = "https://www.acme.ch.put"


@pytest.mark.rest
@pytest.mark.put_request
def test_put() -> None:
    # arrange
    patient_id: Final = 40
    if_match: Final = '"0"'
    geaenderter_patient: Final = {
        "nachname": "Aliceput",
        "email": EMAIL_UPDATE,
        "kategorie": 9,
        "has_newsletter": False,
        "geburtsdatum": "2022-01-09",
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{patient_id}",
        json=geaenderter_patient,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert not response.text


@pytest.mark.rest
@pytest.mark.put_request
def test_put_invalid() -> None:
    # arrange
    patient_id: Final = 40
    geaenderter_patient_invalid: Final = {
        "nachname": "falscher_nachname_put",
        "email": "falsche_email_put@",
        "kategorie": 11,
        "has_newsletter": False,
        "geburtsdatum": "2022-02-04",
        "homepage": "https://?!",
    }
    token: Final = login()
    assert token is not None
    headers = {
        "If-Match": '"0"',
        "Authorization": f"Bearer {token}",
    }

    # act
    response: Final = put(
        f"{rest_url}/{patient_id}",
        json=geaenderter_patient_invalid,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "nachname" in response.text
    assert "email" in response.text
    assert "kategorie" in response.text
    assert "homepage" in response.text


@pytest.mark.rest
@pytest.mark.put_request
def test_put_nicht_vorhanden() -> None:
    # arrange
    patient_id: Final = 999999
    if_match: Final = '"0"'
    geaenderter_patient: Final = {
        "nachname": "Aliceput",
        "email": EMAIL_UPDATE,
        "kategorie": 9,
        "has_newsletter": False,
        "geburtsdatum": "2022-01-03",
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{patient_id}",
        json=geaenderter_patient,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.rest
@pytest.mark.put_request
def test_put_email_exists() -> None:
    # arrange
    patient_id: Final = 40
    if_match: Final = '"1"'
    email_exists: Final = "alice@acme.de"
    geaenderter_patient: Final = {
        "nachname": "Aliceput",
        "email": email_exists,
        "kategorie": 9,
        "has_newsletter": False,
        "geburtsdatum": "2022-01-09",
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{patient_id}",
        json=geaenderter_patient,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert email_exists in response.text


@pytest.mark.rest
@pytest.mark.put_request
def test_put_ohne_versionsnr() -> None:
    # arrange
    patient_id: Final = 40
    geaenderter_patient: Final = {
        "nachname": "Aliceput",
        "email": EMAIL_UPDATE,
        "kategorie": 9,
        "has_newsletter": False,
        "geburtsdatum": "2022-01-03",
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
    }

    # act
    response: Final = put(
        f"{rest_url}/{patient_id}",
        json=geaenderter_patient,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_REQUIRED


@pytest.mark.rest
@pytest.mark.put_request
def test_put_alte_versionsnr() -> None:
    # arrange
    patient_id: Final = 40
    if_match: Final = '"-1"'
    geaenderter_patient: Final = {
        "nachname": "Aliceput",
        "email": EMAIL_UPDATE,
        "kategorie": 9,
        "has_newsletter": False,
        "geburtsdatum": "2022-01-03",
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{patient_id}",
        json=geaenderter_patient,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED


@pytest.mark.rest
@pytest.mark.put_request
def test_put_ungueltige_versionsnr() -> None:
    # arrange
    patient_id: Final = 40
    if_match: Final = '"xy"'
    geaenderter_patient: Final = {
        "nachname": "Aliceput",
        "email": EMAIL_UPDATE,
        "kategorie": 9,
        "has_newsletter": False,
        "geburtsdatum": "2022-01-03",
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{patient_id}",
        json=geaenderter_patient,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED
    assert not response.text


@pytest.mark.rest
@pytest.mark.put_request
def test_put_versionsnr_ohne_quotes() -> None:
    # arrange
    patient_id: Final = 40
    if_match: Final = "0"
    geaenderter_patient: Final = {
        "nachname": "Aliceput",
        "email": EMAIL_UPDATE,
        "kategorie": 9,
        "has_newsletter": False,
        "geburtsdatum": "2022-01-03",
        "homepage": HOMEPAGE_UPDATE,
    }
    token: Final = login()
    assert token is not None
    headers = {
        "Authorization": f"Bearer {token}",
        "If-Match": if_match,
    }

    # act
    response: Final = put(
        f"{rest_url}/{patient_id}",
        json=geaenderter_patient,
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == HTTPStatus.PRECONDITION_FAILED
