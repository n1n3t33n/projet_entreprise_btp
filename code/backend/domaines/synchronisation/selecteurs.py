"""Lectures du domaine synchronisation."""

from typing import Any

from django.db.models import QuerySet

from domaines.synchronisation.models import AnomalieSynchronisation, LotSynchronisation


def lot(id_lot: Any) -> LotSynchronisation:
    """Un lot et ses résultats (rapprochés par ``uuid_evenement``, ET-3)."""
    return LotSynchronisation.objects.prefetch_related("resultats").get(pk=id_lot)


def anomalies(
    statut: str | None = None, type_anomalie: str | None = None
) -> QuerySet[AnomalieSynchronisation]:
    """Anomalies les plus récentes d'abord, avec l'appareil, son propriétaire
    et l'événement qui les a motivées (EF-SYN-05)."""
    requete = AnomalieSynchronisation.objects.select_related(
        "appareil__utilisateur", "resultat_evenement"
    ).order_by("-date_detection")
    if statut:
        requete = requete.filter(statut=statut)
    if type_anomalie:
        requete = requete.filter(type_anomalie=type_anomalie)
    return requete
