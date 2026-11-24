"""Signalement des étapes en retard (RG-A8, EF-AVA-09, Q-AU).

Traitement planifié ``signaler_retards`` (cadre socle/traitements.py), lancé
chaque jour par ``python manage.py lancer_traitement signaler_retards``. Il
annonce chaque étape en retard ; l'avis est unique par étape, donc relancer
le traitement ne prévient personne deux fois.
"""

from django.utils import timezone

from domaines.avancement import selecteurs
from domaines.avancement.services import publications


def signaler() -> str:
    """Corps du traitement planifié ; rend son bilan."""
    en_retard = (
        selecteurs.etapes()
        .filter(selecteurs.filtre_retard(timezone.localdate()))
        .select_related("logement__zone", "etape_modele")
    )
    nombre = 0
    for etape in en_retard:
        publications.en_retard(etape)
        nombre += 1
    return f"{nombre} étape(s) en retard annoncée(s)."
