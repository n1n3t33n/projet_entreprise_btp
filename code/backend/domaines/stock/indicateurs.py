"""Indicateurs du stock pour le pilotage (socle/indicateurs.py).

Rapport hebdomadaire (EF-DSH-06) : mouvements de la période, sorties en
attente de décision, alertes et niveaux à l'instant du calcul. Usage du
pilote (EF-DSH-07) : mouvements saisis et écarts d'inventaire de la période.
Déclarés par ``stock/apps.py``.
"""

from datetime import date

from django.db.models import QuerySet

from domaines.stock import selecteurs
from domaines.stock.constantes import (
    ALERTE_OUVERTE,
    NIVEAU_CRITIQUE,
    NIVEAU_MINIMAL,
    NIVEAU_VIDE,
    TYPE_AJUSTEMENT_MOINS,
    TYPE_AJUSTEMENT_PLUS,
)
from domaines.stock.models import Alerte, MouvementStock, StockCourant
from domaines.stock.services.mouvements import TYPES_RESERVES
from socle.indicateurs import RAPPORT, USAGE, Ligne, Rubrique, bornes


def _periode(debut: date, fin: date) -> QuerySet[MouvementStock]:
    de, a = bornes(debut, fin)
    return MouvementStock.objects.filter(date_operation__gte=de, date_operation__lt=a)


def rapport(debut: date, fin: date) -> list[Ligne]:
    mouvements = _periode(debut, fin)
    stocks = StockCourant.objects.all()
    return [
        ("Entrées de la période", mouvements.filter(type_mouvement__sens__gt=0).count()),
        ("Sorties de la période", mouvements.filter(type_mouvement__sens__lt=0).count()),
        ("Sorties en attente de décision", selecteurs.en_attente().count()),
        ("Alertes de stock ouvertes", Alerte.objects.filter(statut=ALERTE_OUVERTE).count()),
        ("Articles sous le seuil minimal", stocks.filter(niveau_alerte=NIVEAU_MINIMAL).count()),
        (
            "Articles critiques ou vides",
            stocks.filter(niveau_alerte__in=(NIVEAU_CRITIQUE, NIVEAU_VIDE)).count(),
        ),
        ("Articles en stock négatif", stocks.filter(quantite__lt=0).count()),
    ]


def usage(debut: date, fin: date) -> list[Ligne]:
    mouvements = _periode(debut, fin)
    ajustements = (TYPE_AJUSTEMENT_PLUS, TYPE_AJUSTEMENT_MOINS)
    return [
        (
            "Mouvements saisis",
            mouvements.exclude(type_mouvement_id__in=TYPES_RESERVES).count(),
        ),
        (
            "Écarts d'inventaire ajustés",
            mouvements.filter(type_mouvement_id__in=ajustements).count(),
        ),
    ]


RUBRIQUES = (
    Rubrique(RAPPORT, 20, "Stock", rapport),
    Rubrique(USAGE, 10, "Saisie du stock", usage),
)
