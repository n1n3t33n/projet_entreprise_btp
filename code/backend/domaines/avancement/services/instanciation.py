"""Instanciation des étapes d'un logement depuis la gamme (RG-A1, EF-AVA-01).

Les étapes d'un logement sont créées à partir de la gamme ACTIVE de son type,
avec le poids de chaque étape modèle (copié : une version ultérieure de la
gamme ne change pas les logements déjà suivis). Deux déclencheurs (Q-AA) :
la création d'un logement, et la publication d'une gamme pour un type dont
des logements n'ont pas encore d'étapes. Une nouvelle version ne recrée
jamais les étapes existantes : leur historique est conservé.

Rejouable : l'unicité (logement, étape modèle) écarte les doublons.
L'instanciation n'est pas un changement de statut (l'étape naît « à faire ») :
elle n'écrit pas d'événement ; le premier événement est l'affectation (ET-1).
"""

from typing import Any

from domaines.avancement.models import EtapeTravaux
from domaines.organisation import selecteurs as selecteurs_organisation
from domaines.referentiels import selecteurs as selecteurs_referentiels


def generer(logement: Any) -> int:
    """Crée les étapes manquantes du logement ; rend le nombre créé."""
    modeles = selecteurs_referentiels.etapes_modele_actives(logement.type_logement_id)
    existantes = set(
        EtapeTravaux.objects.filter(logement=logement).values_list("etape_modele_id", flat=True)
    )
    nouvelles = [
        EtapeTravaux(logement=logement, etape_modele=modele, poids_effectif=modele.poids)
        for modele in modeles
        if modele.pk not in existantes
    ]
    EtapeTravaux.objects.bulk_create(nouvelles, ignore_conflicts=True)
    return len(nouvelles)


def generer_pour_le_type(code_type_logement: str) -> int:
    """Après la publication d'une gamme : instancie les logements du type qui
    n'ont encore aucune étape (les autres gardent la leur)."""
    total = 0
    sans_etapes = selecteurs_organisation.logements().filter(
        type_logement_id=code_type_logement, etapes_travaux__isnull=True
    )
    for logement in sans_etapes:
        total += generer(logement)
    return total
