# Copyright (C) 2026 - present Juergen Zimmermann, Hochschule Karlsruhe
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

"""Pydantic-Modelle für das Lesen von Patientendaten."""

from typing import Annotated
lazy from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from patient.repository import (
    DEFAULT_PAGE_NUMBER,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    Pageable,
    PatientSuchparameter,
)
lazy from patient.entity import Facharzt, Familienstand, Geschlecht
lazy from patient.service import PatientDTO

__all__ = ["PatientFindModel", "PatientPageModel", "PatientResponseModel"]


class PatientFindModel(BaseModel):
    """Suchparameter und Pagination für die Patientensuche."""

    email: str | None = None
    nachname: str | None = None
    page: Annotated[int, Field(ge=DEFAULT_PAGE_NUMBER)] = DEFAULT_PAGE_NUMBER
    size: Annotated[int, Field(ge=0, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE

    # Keine weiteren Attribute erlaubt
    # unveraenderlich
    # https://pydantic.dev/docs/validation/latest/concepts/config
    # https://pydantic.dev/docs/validation/latest/api/pydantic/config
    model_config = ConfigDict(extra="forbid", frozen=True)

    def to_pageable(self) -> Pageable:
        """Erzeugt die Pagination-Daten aus den validierten Parametern."""
        return Pageable(number=self.page, size=self.size)

    def to_suchparameter(self) -> PatientSuchparameter:
        """Erzeugt Suchparameter für den Service."""
        return PatientSuchparameter(email=self.email, nachname=self.nachname)


class AdresseResponseModel(BaseModel):
    """Adresse als Teil eines Model-Objekts für Patienten als Response.

    Damit beim Konvertieren von `PatientDTO` in `PatientResponseModel` auch die
    Attribute von `AdresseDTO`übernommen werden, ist `ConfigDict(from_attributes=True)`
    notwendig. Siehe
    https://pydantic.dev/docs/validation/latest/concepts/models/#nested-attributes
    """

    plz: str
    ort: str

    model_config = ConfigDict(from_attributes=True, strict=True, extra="forbid")


class PatientResponseModel(BaseModel):
    """Pydantic-Modell für einen gefundenen Patienten.

    FastAPI konvertiert implizit das die Felder in JSON, z.B.
    date als String "2000-01-31" oder Enum CHIRURGIE in "C".
    """

    id: int
    nachname: str
    email: str
    kategorie: int
    has_newsletter: bool
    geburtsdatum: date
    homepage: str | None
    geschlecht: Geschlecht | None
    familienstand: Familienstand | None
    adresse: AdresseResponseModel
    fachaerzte: list[Facharzt]
    username: str

    model_config = ConfigDict(from_attributes=True, strict=True, extra="forbid")
    # https://pydantic.dev/docs/validation/latest/api/pydantic/config/#pydantic.config.ConfigDict

    @classmethod
    def from_dto(cls, patient: PatientDTO) -> PatientResponseModel:
        """Konvertiert ein PatientDTO in ein Pydantic-Modell für einen Response.

        Der Aufruf von `model_validate` erfordert die Übernahme der korrespondierende
        Attributwerte aus dem DTO-Objekt. Dafür ist `ConfigDict(from_attributes=True)`
        notwendig.
        Siehe https://pydantic.dev/docs/validation/latest/concepts/models/#arbitrary-class-instances
        Der Aufwand für (unnötige) Validierung ist dabei minimal:
        https://pydantic.dev/docs/validation/latest/concepts/models/#creating-models-without-validation
        """
        return cls.model_validate(patient)


class PageMetaModel(BaseModel):
    """Metadaten für eine Page mit Patientendaten."""

    size: int
    number: int
    total_elements: int
    total_pages: int


class PatientPageModel(BaseModel):
    """Pydantic-Modell für einen Response bei einer Suche mit Pagination."""

    content: tuple[PatientResponseModel, ...]
    page: PageMetaModel
