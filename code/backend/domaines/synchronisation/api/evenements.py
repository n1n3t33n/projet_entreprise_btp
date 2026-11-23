"""Événement de la synchronisation rejouable par lot (Q-AJ) :
``RESOLUTION_ANOMALIE`` — charge utile ``{"id_anomalie": …}``, corps
équivalent à ``POST /synchronisation/anomalies/{id}/traitement``. Il
remplace le ``RESOLUTION_CONFLIT`` du mobile (F-14). Déclaré par
``synchronisation/apps.py``."""

from datetime import datetime
from typing import Any
from uuid import UUID

from domaines.synchronisation.services import anomalies
from socle.synchronisation import Traitement, TypeEvenement


def resolution(
    _utilisateur: Any, _uuid: UUID, _horodatage: datetime | None, charge: dict[str, Any]
) -> Traitement:
    _anomalie, change = anomalies.traiter(charge.get("id_anomalie"))
    return Traitement(cree=change)


TYPES = (TypeEvenement("RESOLUTION_ANOMALIE", resolution, "anomalies", "MODIFIER"),)
