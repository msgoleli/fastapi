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

"""Tests für DELETE."""

from typing import Final

import pytest
from common_api_test import certificate_path, login, rest_url, timeout
from requests import delete


@pytest.mark.rest
@pytest.mark.delete_request
def test_delete() -> None:
    # arrange
    patient_id: Final = 60
    token: Final = login()
    assert token is not None
    headers: Final = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = delete(
        f"{rest_url}/{patient_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == 204  # ruff: ignore[magic-value-comparison]


@pytest.mark.rest
@pytest.mark.delete_request
def test_delete_not_found() -> None:
    # arrange
    patient_id: Final = 999999
    token: Final = login()
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}

    # act
    response: Final = delete(
        f"{rest_url}/{patient_id}",
        headers=headers,
        timeout=timeout,
        verify=certificate_path,
    )

    # assert
    assert response.status_code == 204  # ruff: ignore[magic-value-comparison]
