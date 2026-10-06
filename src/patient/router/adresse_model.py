# Copyright (C) 2023 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""Pydantic-Model für die Adresse."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from patient.entity import Adresse

__all__ = ["AdresseModel"]


class AdresseModel(BaseModel):
    """Pydantic-Model für die Adresse."""

    plz: Annotated[str, StringConstraints(pattern=r"^\d{5}$")]
    """Postleitzahl"""
    ort: Annotated[str, StringConstraints(max_length=64)]
    """Ort"""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        # https://fastapi.tiangolo.com/tutorial/schema-extra-example
        json_schema_extra={
            "example": {
                "plz": "99999",
                "ort": "Testort",
            },
        },
        # https://docs.pydantic.dev/latest/concepts/strict_mode/#as-a-configuration-value
        strict=True,
        # https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data
        extra="forbid",
        # https://pydantic.dev/docs/validation/latest/concepts/models/#faux-immutability
        frozen=True,
    )

    def to_adresse(self) -> Adresse:
        """Konvertierung in ein Adresse-Objekt für SQLAlchemy.

        :return: Adresse-Objekt für SQLAlchemy
        :rtype: Adresse
        """
        return Adresse(
            id=None,
            plz=self.plz,
            ort=self.ort,
            patient_id=None,
            patient=None,
        )
