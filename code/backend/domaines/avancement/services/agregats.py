"""Agrégats d'avancement (RG-A6, CL-5 ``AvancementAgrege``).

Avancement en % = somme des poids des étapes terminées / somme des poids,
en deux versions : DÉCLARÉ (étapes déclarées ou validées) et VALIDÉ (étapes
validées seulement) — RG-A6 « évite l'optimisme ».

Un agrégat par portée et par cible (Q-V) : logement, zone, chantier, et
corps d'état d'un chantier (cible « id du chantier:code du corps d'état »).
Recalcul immédiat des quatre agrégats touchés à chaque événement (SQ-3 étapes
9 et 14) ; consolidation nocturne de tous les agrégats depuis zéro, par le
traitement planifié ``consolider_avancement`` (Q-AB, I-29), rejouable.

Un événement d'exécution alimente l'agrégat de SON logement (MCD « alimente »
(1,1), H11).
"""

from decimal import Decimal
from typing import Any

from django.db.models import Count, DecimalField, Q, QuerySet, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from domaines.avancement.constantes import (
    PORTEE_CHANTIER,
    PORTEE_CORPS_ETAT,
    PORTEE_LOGEMENT,
    PORTEE_ZONE,
    STATUTS_TERMINES,
    VALIDEE,
)
from domaines.avancement.models import AvancementAgrege, EtapeTravaux
from domaines.organisation import selecteurs as selecteurs_organisation

CENT = Decimal("100")
ZERO = Value(Decimal("0"), output_field=DecimalField(max_digits=14, decimal_places=3))


def agregat(portee: str, id_cible: str) -> AvancementAgrege:
    return AvancementAgrege.objects.get_or_create(portee=portee, id_cible=id_cible)[0]


def agregat_du_logement(logement: Any) -> AvancementAgrege:
    return agregat(PORTEE_LOGEMENT, str(logement.pk))


def cible_corps_etat(id_chantier: Any, code_corps_etat: str) -> str:
    return f"{id_chantier}:{code_corps_etat}"


def pourcentage(part: Decimal, total: Decimal) -> Decimal:
    if not total:
        return Decimal("0.000")
    return (part * CENT / total).quantize(Decimal("0.001"))


def mesurer(etapes: QuerySet[EtapeTravaux]) -> tuple[Decimal, Decimal, int]:
    """(% déclaré, % validé, nombre d'étapes) d'un ensemble d'étapes."""
    mesure = etapes.aggregate(
        total=Coalesce(Sum("poids_effectif"), ZERO),
        declare=Coalesce(Sum("poids_effectif", filter=Q(statut__in=STATUTS_TERMINES)), ZERO),
        valide=Coalesce(Sum("poids_effectif", filter=Q(statut=VALIDEE)), ZERO),
        nombre=Count("pk"),
    )
    return (
        pourcentage(mesure["declare"], mesure["total"]),
        pourcentage(mesure["valide"], mesure["total"]),
        mesure["nombre"],
    )


def _mettre_a_jour(portee: str, id_cible: str, etapes: QuerySet[EtapeTravaux]) -> None:
    declare, valide, nombre = mesurer(etapes)
    AvancementAgrege.objects.update_or_create(
        portee=portee,
        id_cible=id_cible,
        defaults={
            "pourcentage_declare": declare,
            "pourcentage_valide": valide,
            "nombre_etapes": nombre,
            "date_calcul": timezone.now(),
        },
    )


def cibles(
    logement: Any, codes_corps_etat: set[str]
) -> list[tuple[str, str, QuerySet[EtapeTravaux]]]:
    """Les agrégats que fait bouger une étape de ce logement."""
    toutes = EtapeTravaux.objects.all()
    zone = logement.zone
    resultat = [
        (PORTEE_LOGEMENT, str(logement.pk), toutes.filter(logement=logement)),
        (PORTEE_ZONE, str(zone.pk), toutes.filter(logement__zone=zone)),
        (
            PORTEE_CHANTIER,
            str(zone.chantier_id),
            toutes.filter(logement__zone__chantier_id=zone.chantier_id),
        ),
    ]
    for code in codes_corps_etat:
        resultat.append(
            (
                PORTEE_CORPS_ETAT,
                cible_corps_etat(zone.chantier_id, code),
                toutes.filter(
                    logement__zone__chantier_id=zone.chantier_id,
                    etape_modele__corps_etat_id=code,
                ),
            )
        )
    return resultat


def recalculer(logement: Any, codes_corps_etat: set[str]) -> None:
    """Recalcul immédiat des agrégats touchés (RG-A6)."""
    for portee, id_cible, etapes in cibles(logement, codes_corps_etat):
        _mettre_a_jour(portee, id_cible, etapes)


def consolider() -> str:
    """Traitement planifié nocturne : recalcule tous les agrégats depuis les
    étapes (Q-AB, I-29) ; corrige toute dérive, ne change rien s'il n'y en a
    pas."""
    nombre = 0
    for logement in selecteurs_organisation.logements().select_related("zone"):
        codes = set(
            EtapeTravaux.objects.filter(logement=logement).values_list(
                "etape_modele__corps_etat_id", flat=True
            )
        )
        recalculer(logement, codes)
        nombre += 1
    return f"Avancement consolidé pour {nombre} logement(s)."
