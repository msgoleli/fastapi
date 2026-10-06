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

"""Funktionen für E-Mails."""

# https://docs.python.org/3/library/smtplib.html
from email.message import EmailMessage
from email.utils import make_msgid
from smtplib import SMTP, SMTPServerDisconnected
from socket import gaierror
from typing import Final
from uuid import uuid4

from loguru import logger

from patient.config import mail_config, receiver, sender
lazy from patient.service.patient_dto import PatientDTO

__all__ = ["send_mail"]

# WhatsApp-Nachricht durch PyWhatKit: https://github.com/Ankit404butfound/PyWhatKit
# knockknock fuer: SMS, Discord, Slack, Microsoft Teams, Telegram, ...


def send_mail(patient_dto: PatientDTO) -> None:
    """Funktion, um eine E-Mail zu senden.

    :param patient_dto: Patienten-Daten
    """
    logger.debug("{}", patient_dto)
    if not mail_config.enabled:
        logger.warning("send_mail: Der Mailserver ist deaktiviert")
        return

    # https://docs.python.org/3/library/email.examples.html
    msg: Final = EmailMessage()
    msg["From"] = sender
    msg["To"] = (receiver,)
    msg["Subject"] = f"Neuer Patient: ID={patient_dto.id}"
    # https://docs.python.org/3/library/email.utils.html#email.utils.make_msgid
    msg["Message-ID"] = make_msgid(idstring=str(uuid4()))

    msg.set_content(f"Neuer Patient: {patient_dto.nachname}")

    asparagus_cid: Final = make_msgid()
    msg.add_alternative(
        f"Neuer Patient: <b>{patient_dto.nachname}</b>".format(
            asparagus_cid=asparagus_cid[1:-1]
        ),
        subtype="html",
    )

    try:
        # https://docs.python.org/3/library/smtplib.html
        with SMTP(
            host=mail_config.host, port=mail_config.port, timeout=mail_config.timeout
        ) as smtp:
            # ggf. TLS verwenden und einloggen
            # smtp.starttls()
            # smtp.login("my_username", "my_password")
            logger.debug("msg={}", msg)
            smtp.send_message(msg)
    except ConnectionRefusedError:
        # https://docs.python.org/3/library/exceptions.html:
        # ConnectionRefusedError -> ConnectionError -> OSError
        # TODO https://github.com/python/cpython/issues/102414
        logger.warning("ConnectionRefusedError")
    except SMTPServerDisconnected:
        # z.B. bei Timeout
        # https://docs.python.org/3/library/smtplib.html
        # SMTPServerDisconnected -> SMTPException -> OSError
        logger.warning("SMTPServerDisconnected")
    except TimeoutError:
        logger.warning("TimeoutError beim Senden der E-Mail")
    except gaierror:
        # gai = getaddrinfo()  # NOSONAR
        logger.warning("socket.gaierror: Laeuft der Mailserver im virtuellen Netzwerk?")
