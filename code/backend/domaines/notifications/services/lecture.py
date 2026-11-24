"""Lecture des notifications (CL-5 ``Notification.dateLecture``).

Un utilisateur ne marque que SES notifications : celle d'un autre répond
404, comme si elle n'existait pas. Marquer deux fois ne change rien.
"""

from typing import Any

from django.utils import timezone

from domaines.notifications.models import Notification
from socle.api_outils import obtenir_ou_404


def marquer_lue(utilisateur: Any, id_notification: Any) -> Notification:
    notification = obtenir_ou_404(
        Notification.objects.select_related("type_notification"),
        "Cette notification est introuvable.",
        pk=id_notification,
        utilisateur=utilisateur,
    )
    if notification.date_lecture is None:
        notification.date_lecture = timezone.now()
        notification.save(update_fields=["date_lecture"])
    return notification


def tout_lire(utilisateur: Any) -> int:
    """Rend le nombre de notifications marquées lues."""
    return Notification.objects.filter(utilisateur=utilisateur, date_lecture__isnull=True).update(
        date_lecture=timezone.now()
    )
