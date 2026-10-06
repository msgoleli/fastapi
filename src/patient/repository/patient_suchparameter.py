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

"""Filter für die Patientensuche."""

from dataclasses import dataclass

__all__ = ["PatientSuchparameter"]


@dataclass(frozen=True, slots=True, kw_only=True)
class PatientSuchparameter:
    """Suchparameter für die Patientensuche."""

    email: str | None = None
    """Exakte Emailadresse als Suchparameter."""

    nachname: str | None = None
    """Teil des Nachnamens als Suchparameter."""

    def is_empty(self) -> bool:
        """Prüft, ob kein Suchparameter gesetzt ist."""
        return self.email is None and self.nachname is None
