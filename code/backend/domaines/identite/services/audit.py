"""Écriture dans le journal d'audit (RG-D9 ; MPD-1). La lecture est dans
``selecteurs/audit.py``.

Le journal est immuable (RG-S8) : ce service ne fait qu'AJOUTER des entrées.
Il est appelé par les autres services au moment même de l'action sensible,
pour qu'aucune action ne puisse « oublier » sa trace.
"""

from typing import Any

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
