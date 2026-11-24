"""Registre des indicateurs de pilotage (EF-DSH-06, EF-DSH-07, I-29).

Le rapport hebdomadaire et les indicateurs d'usage rassemblent des chiffres
de plusieurs domaines. Pour qu'aucun module n'ait à les connaître tous,
chaque domaine déclare dans son ``apps.ready()`` une rubrique : un titre et
une fonction qui, pour une période [début, fin], rend ses lignes
(indicateur, valeur). Le domaine pilotage les assemble dans l'ordre.

Deux familles : ``RAPPORT`` (rapport hebdomadaire, direction et responsable
technique) et ``USAGE`` (indicateurs d'usage du pilote, administrateur).
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any

from django.utils import timezone

RAPPORT = "RAPPORT"
USAGE = "USAGE"

Ligne = tuple[str, Any]
Calcul = Callable[[date, date], list[Ligne]]


@dataclass(frozen=True)
class Rubrique:
    famille: str
    ordre: int
    titre: str
    calculer: Calcul


RUBRIQUES: dict[tuple[str, str], Rubrique] = {}


def declarer_rubrique(rubrique: Rubrique) -> None:
    """Appelé par un domaine au démarrage. Redéclarer remplace."""
    RUBRIQUES[(rubrique.famille, rubrique.titre)] = rubrique


def bornes(debut: date, fin: date) -> tuple[datetime, datetime]:
    """Période [début 00:00, lendemain de fin 00:00[ dans le fuseau du serveur,
    pour filtrer des horodatages sur des jours entiers."""
    zone = timezone.get_current_timezone()
    return (
        timezone.make_aware(datetime.combine(debut, time.min), zone),
        timezone.make_aware(datetime.combine(fin + timedelta(days=1), time.min), zone),
    )


def rubriques(famille: str) -> list[Rubrique]:
    """Lu au moment du calcul, jamais au chargement d'un module."""
    return sorted((r for r in RUBRIQUES.values() if r.famille == famille), key=lambda r: r.ordre)
