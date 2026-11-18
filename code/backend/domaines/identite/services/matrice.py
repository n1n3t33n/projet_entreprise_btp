"""Matrice des droits : lecture et remplacement (EF-AUT-02, EF-AUT-07, UC-4).

``PUT /api/droits/accordes`` remplace la matrice. Règle de portée du
remplacement : seuls les MODULES concernés sont remplacés — ceux cités par
le champ facultatif ``modules``, à défaut ceux des permissions envoyées. Le
poste web, qui n'affiche que les permissions d'écran, ne peut ainsi jamais
effacer par mégarde les droits « api », « mobile » ou « technique ».

Garde-fou : le rôle ADMINISTRATEUR conserve toujours le droit de modifier la
matrice (sinon plus personne ne pourrait la corriger).
"""

from dataclasses import dataclass
from typing import Any

from django.db import transaction

from domaines.identite.constantes import (
    AUDIT_MODIFICATION_DROITS,
    OBJET_DROITS,
    PORTEES_DROIT,
    ROLE_ADMINISTRATEUR,
)
from domaines.identite.models import DroitAccorde, Permission, Role
from domaines.identite.services import audit
from socle.erreurs import ErreurApi

PERMISSION_GARDEE = "api.droits.modifier"


@dataclass(frozen=True)
class LigneDroit:
    code_role: str
    code_permission: str
    portee: str


def remplacer(
    auteur: Any, lignes: list[LigneDroit], modules: list[str] | None, adresse_ip: str | None
) -> list[DroitAccorde]:
    """Remplace les droits des modules concernés, en une seule transaction."""
    permissions = {p.code_permission: p for p in Permission.objects.all()}
    roles = set(Role.objects.values_list("code_role", flat=True))
    erreurs: dict[str, list[str]] = {}
    for ligne in lignes:
        if ligne.code_role not in roles:
            erreurs.setdefault("role_code_role", []).append(f"Rôle inconnu : {ligne.code_role}")
        if ligne.code_permission not in permissions:
            erreurs.setdefault("permission_code_permission", []).append(
                f"Permission inconnue : {ligne.code_permission}"
            )
        if ligne.portee not in PORTEES_DROIT:
            erreurs.setdefault("portee", []).append(f"Portée inconnue : {ligne.portee}")
    if erreurs:
        raise ErreurApi(
            statut=400,
            motif="DONNEES_INVALIDES",
            message="Certaines lignes de la matrice sont incorrectes.",
            details=erreurs,
        )

    concernes = set(modules or []) | {permissions[ligne.code_permission].module for ligne in lignes}
    if not concernes:
        raise ErreurApi(
            statut=400,
            motif="DONNEES_INVALIDES",
            message="Précisez les modules de droits à remplacer.",
            details={"modules": ["Liste vide."]},
        )
    gardee = permissions.get(PERMISSION_GARDEE)
    if gardee is not None and gardee.module in concernes:
        garde = any(
            ligne.code_role == ROLE_ADMINISTRATEUR and ligne.code_permission == PERMISSION_GARDEE
            for ligne in lignes
        )
        if not garde:
            raise ErreurApi(
                statut=409,
                motif="VERROUILLAGE_ADMINISTRATION",
                message="Le rôle Administrateur doit garder le droit de modifier la matrice.",
            )

    with transaction.atomic():
        DroitAccorde.objects.filter(permission__module__in=concernes).delete()
        uniques = {(ligne.code_role, ligne.code_permission): ligne for ligne in lignes}
        DroitAccorde.objects.bulk_create(
            DroitAccorde(
                role_id=ligne.code_role, permission_id=ligne.code_permission, portee=ligne.portee
            )
            for ligne in uniques.values()
        )
        audit.consigner(auteur, AUDIT_MODIFICATION_DROITS, OBJET_DROITS, adresse_ip)
    return list(DroitAccorde.objects.order_by("role_id", "permission_id"))
