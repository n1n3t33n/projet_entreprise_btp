"""Abonnement du domaine notifications aux événements métier (I-19).

La production se fait dans un point de reprise : si elle échoue, l'opération
métier qui a publié l'événement continue (socle/evenements.publier journalise
l'erreur).
"""

from typing import Any

from django.db import transaction

from domaines.notifications.services import production
from socle.evenements import EvenementMetier


def evenement_publie(sender: Any, evenement: EvenementMetier, **_kwargs: Any) -> None:
    with transaction.atomic():
        production.produire(evenement)
