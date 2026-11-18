"""Lecture typée des variables d'environnement.

Pourquoi : la cible de déploiement est un PaaS (arbitrage Q6), où toute la
configuration arrive par variables d'environnement et jamais par fichier. Ce
module est le seul endroit qui lit ``os.environ`` pour les réglages, afin
qu'une variable manquante échoue tôt avec un message clair, plutôt que de
laisser une valeur par défaut silencieuse en production.
"""

import os

from django.core.exceptions import ImproperlyConfigured


def texte(nom: str, defaut: str | None = None) -> str:
    """Rend la variable ``nom`` ; échoue si elle est absente et sans défaut."""
    valeur = os.environ.get(nom)
    if valeur is None or valeur == "":
        if defaut is None:
            raise ImproperlyConfigured(f"La variable d'environnement {nom} est obligatoire.")
        return defaut
    return valeur


def texte_facultatif(nom: str) -> str | None:
    """Rend la variable ``nom`` ou ``None`` si elle est absente ou vide."""
    valeur = os.environ.get(nom)
    return valeur or None


def entier(nom: str, defaut: int) -> int:
    """Rend la variable ``nom`` convertie en entier."""
    brut = texte(nom, str(defaut))
    try:
        return int(brut)
    except ValueError as erreur:
        raise ImproperlyConfigured(f"La variable {nom} doit être un nombre entier.") from erreur


def booleen(nom: str, defaut: bool) -> bool:
    """Rend la variable ``nom`` interprétée comme vrai/faux (1, true, oui…)."""
    brut = texte(nom, "1" if defaut else "0").strip().lower()
    return brut in {"1", "true", "vrai", "oui", "yes"}


def liste(nom: str, defaut: str = "") -> list[str]:
    """Rend la variable ``nom`` découpée sur les virgules, sans éléments vides."""
    brut = os.environ.get(nom, defaut)
    return [element.strip() for element in brut.split(",") if element.strip()]
