"""Masquage des secrets dans les journaux et les rapports d'erreur.

Exigence 6.1 : un PIN, un jeton, un mot de passe ou tout autre secret ne doit
JAMAIS apparaître dans un journal. La garantie repose sur trois niveaux :
  1. on ne journalise jamais les corps de requête ou de réponse (le journal
     de requête n'émet qu'une liste blanche de champs, voir correlation.py) ;
  2. ce filtre, branché sur le gestionnaire de journaux, masque toute valeur
     dont la clé est sensible et tout jeton « Bearer » dans le texte ;
  3. un test automatique vérifie qu'un mot de passe et un jeton connus
     n'apparaissent dans aucune sortie, y compris en cas d'erreur 500.
"""

import logging
import re
from collections.abc import Mapping
from typing import Any

from django.views.debug import SafeExceptionReporterFilter

MASQUE = "***"

# Clés dont la valeur est toujours masquée (comparaison sans casse, sur une
# partie du nom : « mot_de_passe_initial » est donc masqué aussi).
FRAGMENTS_SENSIBLES = (
    "mot_de_passe",
    "password",
    "pin",
    "jeton",
    "token",
    "authorization",
    "cookie",
    "secret",
    "signature",
    "cle_api",
)

_MOTIF_PORTEUR = re.compile(r"(?i)(bearer\s+)[^\s\"',;]+")
_MOTIF_CLE_VALEUR = re.compile(
    r"(?i)([\"']?(?:" + "|".join(FRAGMENTS_SENSIBLES) + r")[a-z_]*[\"']?\s*[:=]\s*)"
    r"(\"[^\"]*\"|'[^']*'|[^\s,;}]+)"
)


def cle_sensible(cle: object) -> bool:
    """Vrai si la clé désigne une donnée secrète."""
    texte = str(cle).lower()
    return any(fragment in texte for fragment in FRAGMENTS_SENSIBLES)


def masquer_texte(texte: str) -> str:
    """Remplace les jetons porteurs et les couples clé=secret par un masque."""
    texte = _MOTIF_PORTEUR.sub(r"\1" + MASQUE, texte)
    return _MOTIF_CLE_VALEUR.sub(r"\1" + MASQUE, texte)


def masquer_valeur(valeur: Any) -> Any:
    """Masque récursivement une valeur (texte, dictionnaire, liste, tuple)."""
    if isinstance(valeur, str):
        return masquer_texte(valeur)
    if isinstance(valeur, Mapping):
        return {
            cle: (MASQUE if cle_sensible(cle) else masquer_valeur(contenu))
            for cle, contenu in valeur.items()
        }
    if isinstance(valeur, list | tuple):
        return type(valeur)(masquer_valeur(element) for element in valeur)
    return valeur


# Attributs standard d'un LogRecord : jamais considérés comme des « extra ».
_ATTRIBUTS_STANDARD = frozenset(logging.makeLogRecord({}).__dict__) | {"message", "asctime"}


class FiltreMasquage(logging.Filter):
    """Filtre appliqué à tout enregistrement avant son écriture."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = masquer_texte(record.msg)
        if record.args:
            record.args = masquer_valeur(record.args)
        for cle, valeur in list(record.__dict__.items()):
            if cle in _ATTRIBUTS_STANDARD:
                continue
            record.__dict__[cle] = MASQUE if cle_sensible(cle) else masquer_valeur(valeur)
        return True


class FiltreRapportErreur(SafeExceptionReporterFilter):
    """Rapport d'erreur de Django : élargit la liste des réglages masqués."""

    hidden_settings = re.compile(
        "API|TOKEN|KEY|SECRET|PASS|SIGNATURE|HTTP_COOKIE|JETON|MOT_DE_PASSE|PIN",
        flags=re.IGNORECASE,
    )
