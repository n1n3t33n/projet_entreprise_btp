"""Indicateurs de la synchronisation pour le pilotage (socle/indicateurs.py).

Rapport hebdomadaire et usage du pilote (EF-DSH-06, EF-DSH-07 « taux de
synchronisation ») : lots et événements reçus dans la période, taux
d'acceptation, anomalies ouvertes ; pour l'usage, appareils actifs et
appareils synchronisés dans les dernières 24 heures (RG-Y7). Déclarés par
``synchronisation/apps.py``.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from domaines.identite.constantes import STATUT_APPAREIL_ACTIF
from domaines.identite.selecteurs import appareils as selecteurs_appareils
from domaines.synchronisation.constantes import ANOMALIE_OUVERTE
from domaines.synchronisation.models import AnomalieSynchronisation, LotSynchronisation
from socle.indicateurs import RAPPORT, USAGE, Ligne, Rubrique, bornes

FRAICHEUR = timedelta(hours=24)


def _echanges(debut: date, fin: date) -> list[Ligne]:
    de, a = bornes(debut, fin)
    lots = LotSynchronisation.objects.filter(date_reception__gte=de, date_reception__lt=a)
    totaux = lots.aggregate(evenements=Sum("nombre_evenements"), acceptes=Sum("nombre_acceptes"))
    evenements = totaux["evenements"] or 0
    acceptes = totaux["acceptes"] or 0
    taux = (Decimal(acceptes) * 100 / evenements).quantize(Decimal("0.1")) if evenements else None
    return [
        ("Lots de synchronisation reçus", lots.count()),
        ("Opérations reçues du mobile", evenements),
        ("Taux d'acceptation (%)", taux if taux is not None else "—"),
        (
            "Anomalies de synchronisation ouvertes",
            AnomalieSynchronisation.objects.filter(statut=ANOMALIE_OUVERTE).count(),
        ),
    ]


def usage(debut: date, fin: date) -> list[Ligne]:
    actifs = selecteurs_appareils.lister().filter(statut=STATUT_APPAREIL_ACTIF)
    recents = actifs.filter(derniere_synchronisation__gte=timezone.now() - FRAICHEUR)
    return [
        *_echanges(debut, fin),
        ("Appareils actifs", actifs.count()),
        ("Appareils synchronisés depuis 24 h", recents.count()),
    ]


RUBRIQUES = (
    Rubrique(RAPPORT, 30, "Synchronisation", _echanges),
    Rubrique(USAGE, 30, "Synchronisation", usage),
)
