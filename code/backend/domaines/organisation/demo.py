"""Données de démonstration du domaine « organisation » : le chantier pilote
de Grand-Bassam et son magasin central « GB-CENTRAL », tels que les simulent
le web (``lib/mocks/donnees-grand-bassam.ts``) et le mobile."""

from datetime import date

from domaines.organisation.models import Chantier, Magasin
from socle.demo import uid

CODE_CHANTIER = "CH-GB"
CODE_MAGASIN = "GB-CENTRAL"


def charger(mot_de_passe: str) -> dict[str, int]:
    """Crée ou met à jour le chantier et le magasin du pilote."""
    chantier, _ = Chantier.objects.update_or_create(
        id_chantier=uid("chantier", CODE_CHANTIER),
        defaults={
            "code": CODE_CHANTIER,
            "nom": "Chantier de Grand-Bassam",
            "programme": "Programme Grand-Bassam — villas et duplex",
            "date_debut": date(2026, 9, 1),
            "statut": "ACTIF",
        },
    )
    Magasin.objects.update_or_create(
        id_magasin=uid("magasin", CODE_MAGASIN),
        defaults={
            "code": CODE_MAGASIN,
            "nom": "Magasin central",
            "actif": True,
            "chantier": chantier,
        },
    )
    return {"chantier": 1, "magasin": 1}
