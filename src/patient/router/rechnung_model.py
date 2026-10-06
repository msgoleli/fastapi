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

"""Pydantic-Model für die Rechnungen."""

from typing import Annotated
lazy from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from patient.entity import Rechnung

__all__ = ["RechnungModel"]


class RechnungModel(BaseModel):
    """Pydantic-Model für die rechnung_dict."""

    betrag: Decimal = Field(strict=False)
    """Der Betrag. Keine strikte Validierung: JSON -> float in Python."""
    waehrung: Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")]
    """Die Währung."""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        # https://fastapi.tiangolo.com/tutorial/schema-extra-example
        json_schema_extra={
            "example": {
                "betrag": "999.99",
                "waehrung": "EUR",
            },
        },
        # https://docs.pydantic.dev/latest/concepts/strict_mode/#as-a-configuration-value
        strict=True,
        # https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data
        extra="forbid",
        # https://pydantic.dev/docs/validation/latest/concepts/models/#faux-immutability
        frozen=True,
    )

    def to_rechnung(self) -> Rechnung:
        """Konvertierung in ein Rechnung-Objekt für SQLAlchemy.

        :return: Rechnung-Objekt für SQLAlchemy
        :rtype: Rechnung
        """
        return Rechnung(
            id=None,
            betrag=self.betrag,
            waehrung=self.waehrung,
            patient_id=None,
            patient=None,
        )
