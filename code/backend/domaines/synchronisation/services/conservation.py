"""Conservation des données de synchronisation (Q-BF, B7).

Traitement planifié ``purger_synchronisation`` (chaque nuit) :
  1. anomalies TRAITÉES détectées il y a plus de
     ``CONSERVATION_ANOMALIES_TRAITEES_JOURS`` jours ;
  2. lots reçus il y a plus de ``CONSERVATION_LOTS_JOURS`` jours, avec leurs
     résultats, sauf s'ils sont encore cités par une anomalie conservée
     (ouverte ou récente) : elle garde ainsi l'événement qui l'a motivée.
Les opérations elles-mêmes vivent dans les journaux immuables des domaines,
qui ne sont jamais purgés : un lot n'est qu'une trace de transport.
"""

from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from domaines.synchronisation.constantes import ANOMALIE_TRAITEE
from domaines.synchronisation.models import (
    AnomalieSynchronisation,
    LotSynchronisation,
    ResultatEvenement,
)


@transaction.atomic
def purger() -> str:
    maintenant = timezone.now()
    anomalies, _detail = AnomalieSynchronisation.objects.filter(
        statut=ANOMALIE_TRAITEE,
        date_detection__lt=maintenant
        - timedelta(days=settings.CONSERVATION_ANOMALIES_TRAITEES_JOURS),
    ).delete()
    cites = AnomalieSynchronisation.objects.filter(resultat_evenement__isnull=False).values(
        "resultat_evenement__lot_synchronisation_id"
    )
    lots = LotSynchronisation.objects.filter(
        date_reception__lt=maintenant - timedelta(days=settings.CONSERVATION_LOTS_JOURS)
    ).exclude(pk__in=cites)
    resultats, _detail = ResultatEvenement.objects.filter(lot_synchronisation__in=lots).delete()
    nombre_lots, _detail = lots.delete()
    return (
        f"{anomalies} anomalie(s) traitée(s), {nombre_lots} lot(s) et "
        f"{resultats} résultat(s) purgés."
    )
