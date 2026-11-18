"""Formateur JSON des journaux (exigence 6.1).

Une ligne JSON par événement, lisible par n'importe quel agrégateur de la
plateforme d'hébergement, sans dépendance supplémentaire.
"""

import json
import logging
from datetime import UTC, datetime

from socle.journalisation import contexte
from socle.journalisation.masquage import masquer_texte

# Liste blanche des champs « extra » recopiés dans la sortie : rien d'autre ne
# peut fuir, même si un appelant passe un champ inattendu.
CHAMPS_AUTORISES = (
    "id_utilisateur",
    "id_appareil",
    "route",
    "methode",
    "statut",
    "duree_ms",
    "motif",
    "commande",
    "detail",
    # Alertes techniques (6.7) et traitements planifiés (6.5).
    "type_alerte",
    "nom_traitement",
)


class FormateurJson(logging.Formatter):
    """Transforme un enregistrement en une ligne JSON."""

    def format(self, record: logging.LogRecord) -> str:
        donnees: dict[str, object] = {
            "horodatage": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "niveau": record.levelname,
            "journal": record.name,
            "message": record.getMessage(),
            "id_correlation": contexte.id_correlation.get(),
        }
        for champ in CHAMPS_AUTORISES:
            if champ in record.__dict__:
                donnees[champ] = record.__dict__[champ]
        if record.exc_info:
            # Trace complète en cas d'erreur serveur, masquée elle aussi.
            donnees["trace"] = masquer_texte(self.formatException(record.exc_info))
        return json.dumps(donnees, ensure_ascii=False, default=str)
