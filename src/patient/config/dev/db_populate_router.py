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

"""DbPopulateController."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger

from patient.config.dev.db_populate import DbPopulateService, get_db_populate_service
from patient.problem_details import ProblemDetails
from patient.security import Role, RolesRequired, User

__all__ = ["router"]


router: Final = APIRouter()


# "Dependency Injection" durch Depends
@router.api_route(
    path="/db_populate",
    methods=["QUERY"],
    tags=["Admin"],
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
)
async def populate(
    request: Request,
    service: Annotated[DbPopulateService, Depends(get_db_populate_service)],
) -> Response:
    """Die DB mit Testdaten durch einen POST-Request neu zu laden.

    :return: JSON-Datensatz mit der Erfolgsmeldung
    :rtype: Response
    """
    body: Final = await request.body()
    if len(body) > 0:
        logger.error("Kein leerer Request-Body")
        return ProblemDetails.create(
            status_code=status.HTTP_400_BAD_REQUEST,
        ).to_response()

    current_user: Final[User] = request.state.current_user
    logger.warning(
        'REST-Schnittstelle zum Neuladen der DB aufgerufen von "{}"',
        current_user.username,
    )
    service.populate()
    return JSONResponse(content={"db_populate": "success"})
