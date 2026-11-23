"""Jeux de référence du catalogue téléchargés par le mobile (EF-SYN-04).

Mêmes lectures et mêmes formes que les routes REST du catalogue : le
téléphone travaille hors ligne avec exactement ce que le web affiche.
Déclarés par ``referentiels/apps.py`` auprès de ``socle/synchronisation.py``.
"""

from typing import Any

from domaines.referentiels import selecteurs
from domaines.referentiels.api import serialiseurs as s
from socle.synchronisation import JeuReference


def unites(_utilisateur: Any) -> Any:
    return s.UniteSerializer(selecteurs.unites(), many=True).data


def articles(_utilisateur: Any) -> Any:
    return s.ArticleSerializer(selecteurs.articles(), many=True).data


def types_mouvement(_utilisateur: Any) -> Any:
    return s.TypeMouvementSerializer(selecteurs.types_mouvement(), many=True).data


def motifs_blocage(_utilisateur: Any) -> Any:
    return s.MotifBlocageSerializer(selecteurs.motifs_blocage(), many=True).data


JEUX = (
    JeuReference("unites", unites, "unites"),
    JeuReference("articles", articles, "articles"),
    JeuReference("types_mouvement", types_mouvement, "types-mouvement"),
    JeuReference("motifs_blocage", motifs_blocage, "motifs-blocage"),
)
