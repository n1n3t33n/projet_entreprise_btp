"""Titulaires d'un rôle dont le périmètre couvre un lieu (Q-AQ).

Sert aux domaines qui doivent prévenir « le gestionnaire de stock de ce
magasin », « le chef de ce chantier » : affectation en vigueur aujourd'hui,
rôle actif, compte actif, et périmètre qui couvre le lieu (MPD-1
``perimetre`` : global s'il ne vise ni chantier ni magasin ; un périmètre de
chantier couvre aussi les magasins de ce chantier).
"""

from typing import Any
from uuid import UUID

from django.db.models import Q, QuerySet
from django.utils import timezone

from domaines.identite.constantes import STATUT_UTILISATEUR_ACTIF
from domaines.identite.models import Utilisateur


def titulaires(
    code_role: str, id_chantier: UUID | None = None, id_magasin: UUID | None = None
) -> QuerySet[Utilisateur]:
    """Sans lieu (anomalie d'un appareil, rapport du programme) : tous les
    titulaires du rôle, quel que soit leur périmètre."""
    jour = timezone.localdate()
    affectation = (
        Q(affectations__role_id=code_role)
        & Q(affectations__role__actif=True)
        & Q(affectations__date_debut__lte=jour)
        & (Q(affectations__date_fin__isnull=True) | Q(affectations__date_fin__gt=jour))
    )
    if id_chantier is not None or id_magasin is not None:
        affectation &= _couvre(id_chantier, id_magasin)
    return Utilisateur.objects.filter(affectation, statut=STATUT_UTILISATEUR_ACTIF).distinct()


def _couvre(id_chantier: Any, id_magasin: Any) -> Q:
    lieu = Q(
        affectations__perimetre__chantier__isnull=True,
        affectations__perimetre__magasin__isnull=True,
    )
    if id_chantier is not None:
        lieu |= Q(affectations__perimetre__chantier_id=id_chantier)
    if id_magasin is not None:
        lieu |= Q(affectations__perimetre__magasin_id=id_magasin)
    return lieu
