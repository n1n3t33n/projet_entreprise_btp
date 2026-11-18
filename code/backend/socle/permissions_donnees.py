"""Outil des migrations de données qui déclarent des permissions.

Les permissions sont des DONNÉES (tables ``permission`` et ``droit_accorde``
du MPD-1), jamais du code. Chaque domaine déclare les siennes dans sa propre
migration, au moyen de ces deux fonctions, et l'administrateur les reçoit pour
que le système reste administrable sur une base neuve (amorçage). La matrice
métier complète se règle ensuite à l'écran « Matrice des droits ».

Les fonctions reçoivent le registre d'applications de la migration
(``apps``) : elles n'importent aucun modèle, ce qui les garde figées dans le
temps comme toute migration.
"""

from typing import Any

ROLE_AMORCAGE = "ADMINISTRATEUR"


def code(module: str, ressource: str, action: str) -> str:
    """Code d'une permission : « module.ressource.action » (forme du web)."""
    return f"{module}.{ressource}.{action.lower()}"


def declarer(apps: Any, permissions: list[tuple[str, str, str, str]]) -> None:
    """Crée ou met à jour les permissions et les accorde à l'administrateur.
    Chaque élément : (module, ressource, action, libellé)."""
    Permission = apps.get_model("identite", "Permission")
    DroitAccorde = apps.get_model("identite", "DroitAccorde")
    for module, ressource, action, libelle in permissions:
        cle = code(module, ressource, action)
        Permission.objects.update_or_create(
            code_permission=cle,
            defaults={
                "module": module,
                "ressource": ressource,
                "action": action,
                "libelle": libelle,
            },
        )
        DroitAccorde.objects.get_or_create(
            role_id=ROLE_AMORCAGE, permission_id=cle, defaults={"portee": "GLOBALE"}
        )


def retirer(apps: Any, permissions: list[tuple[str, str, str, str]]) -> None:
    """Retour arrière : supprime ces permissions et les droits qui les citent."""
    Permission = apps.get_model("identite", "Permission")
    DroitAccorde = apps.get_model("identite", "DroitAccorde")
    codes = [code(m, r, a) for m, r, a, _libelle in permissions]
    DroitAccorde.objects.filter(permission_id__in=codes).delete()
    Permission.objects.filter(code_permission__in=codes).delete()
