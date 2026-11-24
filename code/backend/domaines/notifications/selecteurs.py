"""Lectures du domaine notifications : les notifications d'un utilisateur,
les plus récentes d'abord (index ``ix_notification_destinataire``)."""

from typing import Any

from django.db.models import QuerySet

from domaines.notifications.models import Notification


def de(utilisateur: Any, non_lues: bool = False) -> QuerySet[Notification]:
    requete = (
        Notification.objects.filter(utilisateur=utilisateur)
        .select_related("type_notification")
        .order_by("-date_creation")
    )
    if non_lues:
        requete = requete.filter(date_lecture__isnull=True)
    return requete


def nombre_non_lues(utilisateur: Any) -> int:
    return Notification.objects.filter(utilisateur=utilisateur, date_lecture__isnull=True).count()
