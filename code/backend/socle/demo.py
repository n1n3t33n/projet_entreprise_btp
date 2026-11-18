"""Registre des chargeurs de données de démonstration.

Chaque domaine fournit son propre chargeur et l'inscrit ici depuis son
``AppConfig.ready`` ; la commande ``charger_demo`` les appelle dans l'ordre
croissant de leur rang. Le socle ne connaît ainsi aucun domaine, et un
domaine ne remplit jamais les tables d'un autre : il lit ce dont il a besoin
par les sélecteurs de ce domaine.

Les identifiants des données de démonstration sont dérivés de leur code
(``uid``) : les recharger met à jour les mêmes lignes au lieu d'en créer.
"""

import uuid
from collections.abc import Callable
from dataclasses import dataclass

ESPACE_DEMO = uuid.UUID("6f1c2d3e-4b5a-4c6d-8e7f-0a1b2c3d4e5f")


def uid(nature: str, cle: str) -> uuid.UUID:
    """Identifiant stable d'une donnée de démonstration (le même à chaque
    chargement), par exemple ``uid("chantier", "CH-GB")``."""
    return uuid.uuid5(ESPACE_DEMO, f"{nature}:{cle}")


@dataclass(frozen=True)
class ChargeurDemo:
    """Chargeur d'un domaine : reçoit le mot de passe commun des comptes de
    démonstration et rend un bilan (nom → nombre de lignes)."""

    rang: int
    domaine: str
    charger: Callable[[str], dict[str, int]]


CHARGEURS: list[ChargeurDemo] = []


def declarer_chargeur(rang: int, domaine: str, charger: Callable[[str], dict[str, int]]) -> None:
    """Inscrit le chargeur d'un domaine. Le rang suit le graphe des
    dépendances : organisation (10) avant identité (20), etc."""
    if any(chargeur.domaine == domaine for chargeur in CHARGEURS):
        return
    CHARGEURS.append(ChargeurDemo(rang, domaine, charger))
    CHARGEURS.sort(key=lambda chargeur: chargeur.rang)
