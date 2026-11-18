"""Évaluation de la matrice des droits (EF-AUT-02, EF-AUT-07 ; CL-1).

Un utilisateur détient un droit si l'une de ses affectations ACTIVES
(``affectation_role``, période [date_debut, date_fin[) porte un rôle ACTIF
auquel la permission est accordée (``droit_accorde``). Chaque droit hérite du
périmètre de l'affectation qui le donne.

La PORTÉE d'un droit est traduite en périmètres couverts par un « résolveur »
enregistré dans ``RESOLVEURS_PORTEE``. Arbitrage Q8 : seules GLOBALE et
PERIMETRE existent aujourd'hui, mais aucune logique ne le suppose ; ajouter
CHANTIER, ZONE ou LOGEMENT en v0.2 consistera à enregistrer un résolveur de
plus. Une portée sans résolveur est une erreur de configuration, jamais
interprétée par défaut.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID

from django.db.models import Q, QuerySet
from django.utils import timezone

from domaines.identite.constantes import PORTEE_GLOBALE, PORTEE_PERIMETRE
from domaines.identite.models import AffectationRole, DroitAccorde


class ToutLeProgramme:
    """Marqueur : le droit couvre tous les périmètres."""

    def __repr__(self) -> str:
        return "ToutLeProgramme"


TOUT_LE_PROGRAMME = ToutLeProgramme()

Couverture = ToutLeProgramme | frozenset[UUID]


def _portee_globale(affectation: AffectationRole) -> Couverture:
    return TOUT_LE_PROGRAMME


def _portee_perimetre(affectation: AffectationRole) -> Couverture:
    return frozenset({affectation.perimetre_id})


# Portée → fonction qui rend ce que couvre un droit accordé par l'affectation.
RESOLVEURS_PORTEE: dict[str, Callable[[AffectationRole], Couverture]] = {
    PORTEE_GLOBALE: _portee_globale,
    PORTEE_PERIMETRE: _portee_perimetre,
}


@dataclass(frozen=True)
class DroitEffectif:
    """Un droit détenu, avec le périmètre qui le justifie."""

    code_permission: str
    module: str
    ressource: str
    action: str
    portee: str
    id_perimetre: UUID
    libelle_perimetre: str


def affectations_actives(utilisateur: Any, jour: date | None = None) -> QuerySet[AffectationRole]:
    """Affectations en vigueur le ``jour`` donné (aujourd'hui par défaut),
    sur des rôles actifs. Période demi-ouverte [date_debut, date_fin[."""
    jour = jour or timezone.localdate()
    return (
        AffectationRole.objects.filter(utilisateur=utilisateur, role__actif=True)
        .filter(date_debut__lte=jour)
        .filter(Q(date_fin__isnull=True) | Q(date_fin__gt=jour))
        .select_related("role", "perimetre", "perimetre__chantier", "perimetre__magasin")
        .order_by("-date_debut", "role_id")
    )


def droits_effectifs(utilisateur: Any) -> list[DroitEffectif]:
    """Tous les droits de l'utilisateur, calculés une fois par requête (le
    résultat est gardé sur l'objet utilisateur, qui vit le temps de la
    requête)."""
    en_cache = getattr(utilisateur, "_droits_effectifs", None)
    if en_cache is not None:
        return list(en_cache)
    if not getattr(utilisateur, "is_authenticated", False) or not utilisateur.is_active:
        return []
    affectations = list(affectations_actives(utilisateur))
    roles = {affectation.role_id for affectation in affectations}
    accordes: dict[str, list[DroitAccorde]] = {}
    for droit in DroitAccorde.objects.filter(role_id__in=roles).select_related("permission"):
        accordes.setdefault(droit.role_id, []).append(droit)
    resultat: dict[tuple[str, UUID], DroitEffectif] = {}
    for affectation in affectations:
        for droit in accordes.get(affectation.role_id, []):
            permission = droit.permission
            resultat.setdefault(
                (permission.code_permission, affectation.perimetre_id),
                DroitEffectif(
                    code_permission=permission.code_permission,
                    module=permission.module,
                    ressource=permission.ressource,
                    action=permission.action,
                    portee=droit.portee,
                    id_perimetre=affectation.perimetre_id,
                    libelle_perimetre=affectation.perimetre.libelle,
                ),
            )
    droits = sorted(resultat.values(), key=lambda d: (d.module, d.ressource, d.action))
    utilisateur._droits_effectifs = tuple(droits)
    return droits


def a_le_droit(utilisateur: Any, module: str, ressource: str, action: str) -> bool:
    """Vrai si l'utilisateur détient (module, ressource, action)."""
    return any(
        d.module == module and d.ressource == ressource and d.action == action
        for d in droits_effectifs(utilisateur)
    )


def couverture(utilisateur: Any, module: str, ressource: str, action: str) -> Couverture:
    """Ce que couvre un droit pour cet utilisateur : tout le programme, ou
    l'ensemble des périmètres autorisés (vide s'il n'a pas le droit)."""
    perimetres: set[UUID] = set()
    for affectation in affectations_actives(utilisateur):
        for droit in DroitAccorde.objects.filter(
            role_id=affectation.role_id,
            permission__module=module,
            permission__ressource=ressource,
            permission__action=action,
        ):
            resolveur = RESOLVEURS_PORTEE.get(droit.portee)
            if resolveur is None:
                raise LookupError(f"Aucune règle n'interprète la portée « {droit.portee} ».")
            portee = resolveur(affectation)
            if isinstance(portee, ToutLeProgramme):
                return TOUT_LE_PROGRAMME
            perimetres |= portee
    return frozenset(perimetres)


def oublier_droits(utilisateur: Any) -> None:
    """Efface le calcul gardé sur l'objet (après une modification)."""
    if hasattr(utilisateur, "_droits_effectifs"):
        del utilisateur._droits_effectifs
