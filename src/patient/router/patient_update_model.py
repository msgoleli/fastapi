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

"""Pydantic-Model zum Aktualisieren von Patientendaten."""

from typing import Annotated
lazy from datetime import date

from loguru import logger
from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, StringConstraints

from patient.entity import Facharzt, Familienstand, Geschlecht, Patient

__all__ = ["PatientUpdateModel"]


class PatientUpdateModel(BaseModel):
    """Pydantic-Model zum Aktualisieren von Patientendaten."""

    # https://docs.pydantic.dev/latest/usage/types
    nachname: Annotated[
        str,
        StringConstraints(
            pattern="^[A-ZÄÖÜ][a-zäöüß]+(-[A-ZÄÖÜ][a-zäöüß])?$",
            max_length=64,
        ),
    ]
    """Der Nachname."""
    email: EmailStr
    """Die eindeutige Emailadresse."""
    kategorie: Annotated[int, Field(ge=1, le=9)]
    """Die Kategorie."""
    has_newsletter: bool
    """Angabe, ob der Newsletter abonniert ist."""
    geburtsdatum: date = Field(strict=False)
    """Das Geburtsdatum. Keine strikte Validierung: String in JSON."""
    geschlecht: Geschlecht | None = Field(default=None, strict=False)
    """Das optionale Geschlecht. Keine strikte Validierung: String in JSON."""
    familienstand: Familienstand | None = Field(default=None, strict=False)
    """Der optionale Familienstand. Keine strikte Validierung: String in JSON."""
    homepage: HttpUrl | None = None
    """Die optionale URL der Homepage."""

    model_config = ConfigDict(
        # Beispiel fuer OpenAPI
        # https://fastapi.tiangolo.com/tutorial/schema-extra-example
        json_schema_extra={
            "example": {
                "nachname": "Test",
                "email": "test@acme.com",
                "kategorie": 1,
                "has_newsletter": True,
                "geburtsdatum": "2023-01-31",
                "geschlecht": "W",
                "familienstand": "L",
                "homepage": "https://test.rest",
            },
        },
        # https://docs.pydantic.dev/latest/concepts/strict_mode/#as-a-configuration-value
        strict=True,
        # https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data
        extra="forbid",
        # https://pydantic.dev/docs/validation/latest/concepts/models/#faux-immutability
        frozen=True,
    )

    def to_patient(
        self,
        *,
        fachaerzte: list[Facharzt] | None = None,
    ) -> Patient:
        """Konvertierung in ein Patient-Objekt für SQLAlchemy.

        Argument `fachaerzte`, weil `Patient.fachaerzte` wegen der JSON-Konvertierung
        vom Typ `InitVar` ist.
        :return: Patient-Objekt für SQLAlchemy ohne Adresse, Rechnungen und Fachärzte.
        :rtype: Patient
        """
        logger.debug("self={}", self)
        patient = Patient(
            id=None,
            nachname=self.nachname,
            email=self.email,
            kategorie=self.kategorie,
            has_newsletter=self.has_newsletter,
            geburtsdatum=self.geburtsdatum,
            geschlecht=self.geschlecht,
            familienstand=self.familienstand,
            # HttpUrl ist ungeeignet fuer SQLAlchemy
            homepage=str(self.homepage) if self.homepage is not None else None,
            adresse=None,
            rechnungen=[],
            fachaerzte=fachaerzte,
            username=None,
            erzeugt=None,
            aktualisiert=None,
        )
        logger.debug("patient={}", patient)
        return patient
