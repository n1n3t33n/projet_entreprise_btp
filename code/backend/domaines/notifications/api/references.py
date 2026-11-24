"""Jeu de référence ``notifications`` téléchargé par le mobile (Q-AW) : les
notifications non lues de l'utilisateur, à la forme de
``GET /api/notifications?non_lues=true``. Déclaré par ``notifications/apps.py``
auprès de ``socle/synchronisation.py`` ; la lecture passe par REST."""

from typing import Any

from domaines.notifications import selecteurs
from domaines.notifications.api.serialiseurs import LIMITE_MAXIMALE, NotificationSerializer
from socle.synchronisation import JeuReference


def non_lues(utilisateur: Any) -> Any:
    lignes = selecteurs.de(utilisateur, non_lues=True)[:LIMITE_MAXIMALE]
    return NotificationSerializer(lignes, many=True).data


JEUX = (JeuReference("notifications", non_lues, "notifications"),)
