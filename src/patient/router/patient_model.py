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

"""Pydantic-Model für die Patientendaten."""

from typing import Annotated, Final, override

from loguru import logger
from pydantic import ConfigDict, Field, StringConstraints

from patient.router.patient_update_model import PatientUpdateModel
lazy from patient.entity import Facharzt, Patient
lazy from patient.router.adresse_model import AdresseModel
lazy from patient.router.rechnung_model import RechnungModel

__all__ = ["PatientModel"]


# https://towardsdatascience.com/pydantic-or-dataclasses-why-not-both-convert-between-them-ba382f0f9a9c
class PatientModel(PatientUpdateModel):
    """Pydantic-Model für die Patientendaten."""

    adresse: AdresseModel
    """Die zugehörige Adresse."""
    rechnungen: list[RechnungModel]
    """Die Liste der Rechnungen."""
    fachaerzte: list[Annotated[Facharzt, Field(strict=False)]]
    """Die Liste mit Fachärzten als Enum-Werte."""
    # https://docs.pydantic.dev/usage/types
    username: Annotated[str, StringConstraints(max_length=20)]
    """Der Benutzername für Login."""

    # https://docs.pydantic.dev/latest/concepts/strict_mode/#as-a-configuration-value
    # https://pydantic.dev/docs/validation/latest/concepts/models/#extra-data
    # https://pydantic.dev/docs/validation/latest/concepts/models/#faux-immutability
    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    @override
    def to_patient(
        self,
        *,
        fachaerzte: list[Facharzt] | None = None,
    ) -> Patient:
        """Konvertierung in ein Patient-Objekt für SQLAlchemy.

        :return: Patient-Objekt für SQLAlchemy
        :rtype: Patient
        """
        logger.debug("self={}", self)
        patient: Final = super().to_patient(
            fachaerzte=self.fachaerzte if self.fachaerzte is not None else [],
        )
        patient.adresse = self.adresse.to_adresse()
        patient.rechnungen = [
            rechnung_model.to_rechnung() for rechnung_model in self.rechnungen
        ]
        patient.username = self.username
        logger.debug("patient={}", patient)
        return patient
