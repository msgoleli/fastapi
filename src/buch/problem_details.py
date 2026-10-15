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

"""ProblemDetails gemäß RFC 7807."""

from dataclasses import asdict, dataclass
from typing import Any

from fastapi.responses import JSONResponse
lazy from fastapi import Response

__all__ = ["ProblemDetails"]

BAD_REQUEST = 400
UNAUTHORIZED = 401
FORBIDDEN = 403
PRECONDITION_FAILED = 412
UNPROCESSABLE_CONTENT = 422
PRECONDITION_REQUIRED = 428


@dataclass(frozen=True, eq=False, slots=True, kw_only=True)
class ProblemDetails:
    """Datenstruktur für ProblemDetails gemäß RFC 7807."""

    title: str
    status_code: int
    detail: list[dict[str, Any]] | str | None

    @classmethod
    def create(  # ruff: ignore[too-many-return-statements]
        cls,
        status_code: int,
        # TODO frozendict https://github.com/facebook/pyrefly/issues/4994
        detail: list[dict[str, Any]] | str | None = None,
    ) -> ProblemDetails:
        """ProblemDetails gemäß RFC 7807 erstellen."""
        match status_code:
            case 400:
                return cls(title="Bad Request", status_code=status_code, detail=detail)
            case 401:
                return cls(title="Unauthorized", status_code=status_code, detail=detail)
            case 403:
                return cls(title="Forbidden", status_code=status_code, detail=detail)
            case 412:
                return cls(
                    title="Precondition Failed",
                    status_code=status_code,
                    detail=detail,
                )
            case 422:
                return cls(
                    title="Unprocessable Content",
                    status_code=status_code,
                    detail=detail,
                )
            case 428:
                return cls(
                    title="Precondition Required",
                    status_code=status_code,
                    detail=detail,
                )
            case _:
                return cls(title="Client Error", status_code=status_code, detail=detail)

    def to_response(self) -> Response:
        """ProblemDetails als Response zurückgeben.

        :return: Response mit ProblemDetails als JSON-Datensatz.
        :rtype: Response
        """
        return JSONResponse(
            status_code=self.status_code,
            content=asdict(obj=self),
            media_type="application/problem+json",
        )
