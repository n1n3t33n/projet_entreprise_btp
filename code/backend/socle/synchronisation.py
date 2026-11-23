"""Registre des types d'événements synchronisables (EF-SYN-02, SQ-2).

Le téléphone saisit hors ligne puis envoie ses événements par lots. Le
socle ne connaît aucun domaine : chaque domaine déclare dans son
``apps.ready()`` les types qu'il sait rejouer, avec le droit qu'ils exigent
(le stock : mouvement et décision ; l'avancement : déclaration, blocage,
levée, contrôle). Le service des lots (domaine synchronisation) les appelle
un à un.

Un traitement reçoit l'auteur, l'identifiant de l'événement (créé par le
téléphone, gage d'idempotence), l'heure de saisie sur l'appareil et la charge
utile — exactement le corps de la route REST correspondante (Q-AE) : une
seule règle métier, deux chemins d'entrée. Il lève ``ErreurApi`` ou une
erreur de validation pour refuser ; il rend s'il a créé quelque chose et les
anomalies à signaler (stock devenu négatif, par exemple).
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class Traitement:
    """Issue d'un événement accepté. ``cree`` est faux pour un événement déjà
    reçu par un autre chemin (route REST ou lot précédent)."""

    cree: bool
    anomalies: tuple[tuple[str, str], ...] = field(default_factory=tuple)


Gestionnaire = Callable[[Any, UUID, datetime | None, dict[str, Any]], Traitement]


@dataclass(frozen=True)
class TypeEvenement:
    code: str
    traiter: Gestionnaire
    # Droit exigé : api.<ressource>.<action> (EF-AUT-07).
    ressource: str
    action: str


TYPES: dict[str, TypeEvenement] = {}


def declarer_type(type_evenement: TypeEvenement) -> None:
    """Appelé par un domaine au démarrage. Redéclarer remplace."""
    TYPES[type_evenement.code] = type_evenement
