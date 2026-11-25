"""Publication des événements métier (I-19, Q-AO).

Un domaine annonce ce qui vient de se passer (une alerte de stock s'ouvre,
une étape est rejetée…) sans savoir qui écoute. Le domaine notifications
s'abonne à ``evenement_publie`` ; demain un autre pourrait le faire. La
dépendance reste dans un seul sens : l'émetteur ne connaît que le socle.

L'événement est publié DANS la transaction de l'opération : si elle est
annulée (point de reprise d'un lot de synchronisation, par exemple), ce que
les abonnés ont écrit en base l'est aussi.
"""

import logging
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from django.dispatch import Signal

journal = logging.getLogger(__name__)

evenement_publie = Signal()


@dataclass(frozen=True)
class EvenementMetier:
    """``code`` : nature de l'événement (même code que le type de notification
    qui lui correspond). ``personne`` : l'utilisateur directement concerné
    (auteur de la déclaration rejetée…). ``auteur`` : celui qui a agi, qu'on
    ne prévient pas de sa propre action. ``unique`` : un seul avis par objet
    (une étape en retard n'est signalée qu'une fois). ``contexte`` : champs
    des modèles de message."""

    code: str
    id_objet: UUID | None = None
    id_chantier: UUID | None = None
    id_magasin: UUID | None = None
    # Logement visé : seul son acquéreur est prévenu (RG-D10).
    id_logement: UUID | None = None
    id_alerte: UUID | None = None
    personne: Any = None
    auteur: Any = None
    unique: bool = False
    contexte: dict[str, Any] = field(default_factory=dict)


def publier(evenement: EvenementMetier) -> None:
    """Annonce l'événement aux abonnés. Un abonné défaillant ne fait jamais
    échouer l'opération métier : l'erreur est journalisée, puis oubliée."""
    for _recepteur, resultat in evenement_publie.send_robust(sender=None, evenement=evenement):
        if isinstance(resultat, Exception):
            journal.error("Abonné en échec pour l'événement %s", evenement.code, exc_info=resultat)
