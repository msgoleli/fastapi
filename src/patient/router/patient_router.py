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

"""PatientGetRouter."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger

from patient.router.constants import ETAG, IF_NONE_MATCH, IF_NONE_MATCH_MIN_LEN
from patient.router.dependencies import get_service
from patient.router.patient_find_model import (
    PatientFindModel,
    PatientPageModel,
    PatientResponseModel,
)
from patient.security import Role, RolesRequired, User
lazy from patient.service import PatientService

__all__ = ["patient_router"]


# APIRouter auf Basis der Klasse Router von Starlette
patient_router: Final = APIRouter(tags=["Lesen"])


@patient_router.get(
    path="/{patient_id}",
    dependencies=[Depends(RolesRequired([Role.ADMIN, Role.PATIENT]))],
    response_model=PatientResponseModel,
)
def get_by_id(
    patient_id: int,
    request: Request,
    service: Annotated[PatientService, Depends(get_service)],
) -> Response:
    """Suche mit der Patient-ID.

    :param patient_id: ID des gesuchten Patienten als Pfadparameter
    :param request: Injiziertes Request-Objekt von FastAPI bzw. Starlette
        mit ggf. If-None-Match im Header
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit dem gefundenen Patientendatensatz
    :rtype: Response
    :raises NotFoundError: Falls kein Patient gefunden wurde
    :raises ForbiddenError: Falls die Patientendaten nicht gelesen werden dürfen
    """
    # User-Objekt ist durch Depends(RolesRequired()) in Request.state gepuffert
    user: Final[User] = request.state.current_user
    logger.debug("patient_id={}, user={}", patient_id, user)

    patient: Final = service.find_by_id(patient_id=patient_id, user=user)
    logger.debug("{}", patient)

    if_none_match: Final = request.headers.get(IF_NONE_MATCH)
    if (
        if_none_match is not None
        and len(if_none_match) >= IF_NONE_MATCH_MIN_LEN
        and if_none_match.startswith('"')
        and if_none_match.endswith('"')
    ):
        version = if_none_match[1:-1]
        logger.debug("version={}", version)
        if version is not None:
            try:
                if int(version) == patient.version:
                    return Response(status_code=status.HTTP_304_NOT_MODIFIED)
            except ValueError:
                logger.debug("invalid version={}", version)

    patient_model: Final = PatientResponseModel.from_dto(patient)
    return JSONResponse(
        content=patient_model.model_dump(mode="json"),
        headers={ETAG: f'"{patient.version}"'},
    )


@patient_router.get(
    path="",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
    response_model=PatientPageModel,
)
def get(
    find_model: Annotated[PatientFindModel, Query()],
    service: Annotated[PatientService, Depends(get_service)],
) -> PatientPageModel:
    """Suche mit Query-Parameter.

    Siehe https://fastapi.tiangolo.com/tutorial/query-params und
    https://fastapi.tiangolo.com/de/tutorial/query-param-models
    :param find_model: Validierte Such- und Pagination-Parameter als Pydantic-Model
    :param service: Injizierter Service für Geschäftslogik
    :return: Eine Seite mit Patienten-Daten
    :raises NotFoundError: Falls keine Patienten gefunden wurden
    """
    logger.debug("search={}", find_model)
    result: Final = _find_page(service=service, find_model=find_model)
    logger.debug("result={}", result)
    return result


# TODO https://github.com/fastapi/fastapi/issues/12965
@patient_router.api_route(
    path="/query",
    methods=["QUERY"],
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
    response_model=PatientPageModel,
)
def query(
    find_model: PatientFindModel,
    service: Annotated[PatientService, Depends(get_service)],
) -> PatientPageModel:
    """Suche mit HTTP-Methode _QUERY_.

    **BEACHTE**: HTTP-Methode QUERY ist in FastAPI noch nicht "nativ" implementiert
    https://github.com/fastapi/fastapi/issues/12965 und
    https://www.rfc-editor.org/info/rfc10008
    :param find_model: Validierte Suchparameter (einschließlich Pagination) als
    Pydantic-Model aus dem Request-Body
    :param service: Injizierter Service für Geschäftslogik
    :return: Eine Seite mit Patienten-Daten
    :raises NotFoundError: Falls keine Patienten gefunden wurden
    """
    logger.debug("search={}", find_model)
    result: Final = _find_page(service=service, find_model=find_model)
    logger.debug("result={}", result)
    return result


@patient_router.get(
    path="/nachnamen/{teil}",
    dependencies=[Depends(RolesRequired(Role.ADMIN))],
    response_model=list[str],
)
def get_nachnamen(
    teil: str,
    service: Annotated[PatientService, Depends(get_service)],
) -> list[str]:
    """Suche Nachnamen zum gegebenen Teilstring.

    :param teil: Teilstring der gefundenen Nachnamen
    :param service: Injizierter Service für Geschäftslogik
    :return: Response mit Statuscode 200 und gefundenen Nachnamen im Body
    :rtype: Response
    :raises NotFoundError: Falls keine Nachnamen gefunden wurden
    """
    logger.debug("teil={}", teil)
    nachnamen: Final = service.find_nachnamen(teil=teil)
    return list(nachnamen)


def _find_page(
    service: PatientService,
    find_model: PatientFindModel,
) -> PatientPageModel:
    pageable: Final = find_model.to_pageable()
    patient_slice: Final = service.find(
        suchparameter=find_model.to_suchparameter(),
        pageable=pageable,
    )

    patient_models: Final = tuple(
        PatientResponseModel.from_dto(patient) for patient in patient_slice.content
    )

    total_pages: Final = (
        (patient_slice.total_elements + pageable.size - 1) // pageable.size
        if pageable.size > 0
        else 1
    )

    return PatientPageModel(
        content=patient_models,
        page={
            "size": pageable.size,
            "number": pageable.number,
            "total_elements": patient_slice.total_elements,
            "total_pages": total_pages,
        },
    )
