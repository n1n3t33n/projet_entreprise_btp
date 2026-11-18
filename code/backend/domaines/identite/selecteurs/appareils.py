"""Lecture des appareils enrôlés (écran « Appareils » du web, ET-4)."""

from django.db.models import QuerySet

from domaines.identite.models import Appareil


def lister() -> QuerySet[Appareil]:
    """Appareils avec leur propriétaire, joint en une seule requête."""
    return Appareil.objects.select_related("utilisateur").order_by("utilisateur__nom", "plateforme")
