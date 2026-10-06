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

"""Konfiguration für Mailserver."""

from dataclasses import dataclass
from email.headerregistry import Address
from typing import Final

from loguru import logger

from patient.config.config import app_config

__all__ = ["mail_config", "receiver", "sender"]


_mail_toml: Final = app_config.get("mail", {})


@dataclass(frozen=True, eq=False, slots=True)
class MailConfig:
    """Konfiguration für Mailserver."""

    enabled: bool = bool(_mail_toml.get("enabled", True))
    """True, falls der Mailserver aktiviert ist."""

    host: str = _mail_toml.get("host", "mail")
    """Rechnername des Mailservers."""

    port: int = _mail_toml.get("port", 25)
    """Port des Mailservers."""

    timeout: float = _mail_toml.get("timeout", 1.0)
    """Timeout für den Mailserver in Sekunden."""


mail_config: Final = MailConfig()
logger.debug("mail_config={}", mail_config)


# https://datatracker.ietf.org/doc/html/rfc822.html
sender: Final[Address] = Address(
    display_name="Python Server", username="python.server", domain="acme.com"
)
"""Absender der E-Mails."""

receiver: Final[Address] = Address(
    display_name="Buchhaltung", username="buchhaltung", domain="acme.com"
)
"""Empfänger der E-Mails."""
