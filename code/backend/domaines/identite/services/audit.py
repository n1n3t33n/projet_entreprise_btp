"""Écriture et lecture du journal d'audit (RG-D9, EF-AUT-08 ; MPD-1).

Le journal est immuable (RG-S8) : ce service ne fait qu'AJOUTER des entrées.
Il est appelé par les autres services au moment même de l'action sensible,
pour qu'aucune action ne puisse « oublier » sa trace.
"""

from typing import Any

from django.db.models import QuerySet

from domaines.identite.constantes import LIBELLES_AUDIT
from domaines.identite.models import JournalAudit


def consigner(
    utilisateur: Any, action: str, type_objet: str, adresse_ip: str | None = None
) -> JournalAudit:
    """Ajoute une entrée au journal d'audit (insertion forcée : jamais de
    mise à jour, que les déclencheurs refuseraient de toute façon)."""
    return JournalAudit.objects.create(
        utilisateur=utilisateur,
        action=action,
        type_objet=type_objet,
        adresse_ip=adresse_ip,
    )


def resume(entree: JournalAudit) -> str:
    """Phrase lisible pour l'écran « Journal d'audit » : jamais un code
    interne (charte § 8)."""
    return LIBELLES_AUDIT.get(entree.action, "Action enregistrée")


def lister(
    action: str | None = None, id_auteur: str | None = None, limite: int = 200
) -> QuerySet[JournalAudit]:
    """Entrées les plus récentes d'abord, filtrées par action et auteur
    (EF-AUT-08 : filtres acteur, date, action)."""
    entrees = JournalAudit.objects.select_related("utilisateur").order_by("-horodatage")
    if action:
        entrees = entrees.filter(action=action)
    if id_auteur:
        entrees = entrees.filter(utilisateur_id=id_auteur)
    return entrees[:limite]
