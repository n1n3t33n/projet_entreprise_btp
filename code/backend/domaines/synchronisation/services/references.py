"""Téléchargement incrémental des données de référence (EF-SYN-04, Q-AI).

Le téléphone déclare, pour chaque jeu (catalogue, stock, fiches de route…),
la version qu'il détient. Le serveur l'enregistre dans ``curseur_reference``
(« positionne », MCD) et ne renvoie que les jeux dont la version a changé,
chacun en entier : suffisant pour le pilote (60 articles, 120 étapes). Le
delta ligne à ligne est une dette à traiter avant les gros chantiers
(ENF-04).

La version est une empreinte du contenu : elle change dès qu'une donnée
change, sans compteur à entretenir dans chaque domaine.
"""

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from django.utils import timezone

from domaines.identite.models import Appareil
from domaines.identite.services.droits import a_le_droit
from domaines.synchronisation.models import CurseurReference
from socle.synchronisation import REFERENCES

# 15 chiffres hexadécimaux : la version tient dans le bigint du MPD.
CHIFFRES_VERSION = 15
# Plus grande version possible, et sa longueur en chiffres décimaux (19) :
# la route refuse une version plus longue sans la convertir.
VERSION_MAX = 16**CHIFFRES_VERSION - 1
CHIFFRES_DECIMAUX_VERSION = len(str(VERSION_MAX))


@dataclass(frozen=True)
class Jeu:
    type_donnee: str
    version: int
    donnees: Any


def empreinte(donnees: Any) -> int:
    texte = json.dumps(donnees, sort_keys=True, default=str, ensure_ascii=False)
    return int(hashlib.sha256(texte.encode()).hexdigest()[:CHIFFRES_VERSION], 16)


def telecharger(
    utilisateur: Any, appareil: Appareil, versions_connues: dict[str, int]
) -> tuple[list[Jeu], list[str]]:
    """Rend (jeux changés, codes des jeux inchangés). Seuls les jeux couverts
    par les droits de l'utilisateur sont proposés."""
    changes: list[Jeu] = []
    inchanges: list[str] = []
    for code, jeu in sorted(REFERENCES.items()):
        if not a_le_droit(utilisateur, "api", jeu.ressource, jeu.action):
            continue
        connue = versions_connues.get(code, 0)
        _positionner(appareil, code, connue)
        donnees = jeu.fournir(utilisateur)
        version = empreinte(donnees)
        if version == connue:
            inchanges.append(code)
        else:
            changes.append(Jeu(code, version, donnees))
    return changes, inchanges


def _positionner(appareil: Appareil, code: str, version: int) -> None:
    CurseurReference.objects.update_or_create(
        appareil=appareil,
        type_donnee=code,
        defaults={"version_connue": version, "date_mise_a_jour": timezone.now()},
    )
