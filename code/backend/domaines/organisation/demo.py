"""Données de démonstration du domaine « organisation » : le chantier pilote
de Grand-Bassam, son magasin « GB-CENTRAL », ses trois îlots et ses douze
logements, ses types de logement et ses paramètres, tels que les simule le web
(``lib/mocks/donnees-grand-bassam.ts``, ``avancement-grand-bassam.ts``,
``gammes-grand-bassam.ts``, ``parametrage-grand-bassam.ts``).

Différences voulues avec le web : statut des logements dans leur cycle de vie
{A_VENIR, EN_COURS, LIVRE} (Q-A) ; paramètre ``delai_relance_validation_h``
ajouté (Q-F), absent du web ; paramètres RG-S10 et RG-S11 ajoutés en B3.
"""

from datetime import date

from domaines.organisation.constantes import (
    CLE_DELAI_RELANCE_VALIDATION,
    STATUT_LOGEMENT_A_VENIR,
    STATUT_LOGEMENT_EN_COURS,
    STATUT_LOGEMENT_LIVRE,
    TYPE_ZONE_TRANCHE,
)
from domaines.organisation.models import (
    Chantier,
    Logement,
    Magasin,
    ParametreChantier,
    TypeLogement,
    Zone,
)
from socle.demo import uid

CODE_CHANTIER = "CH-GB"
CODE_MAGASIN = "GB-CENTRAL"

TYPES_LOGEMENT = [
    ("VILLA3", "Villa 3 pièces"),
    ("VILLA4", "Villa 4 pièces"),
    ("DUPLEX", "Duplex"),
]
ZONES = [("A", "Îlot A"), ("B", "Îlot B"), ("C", "Îlot C")]

# (clé, valeur, type, libellé) — les cinq paramètres du web, plus le délai de
# relance des mouvements sans décision (ET-2, 24 h).
PARAMETRES = [
    ("delai_synchro_alerte_h", "24", "ENTIER", "Seuil d'alerte de synchronisation (heures)"),
    ("poids_total_cible", "100", "ENTIER", "Poids total attendu d'une gamme"),
    (
        "autoriser_stock_negatif",
        "true",
        "BOOLEEN",
        "Autoriser un stock négatif (signalé comme anomalie)",
    ),
    ("devise", "XOF", "TEXTE", "Devise du chantier"),
    ("tva_pourcent", "18.00", "DECIMAL", "Taux de TVA (%)"),
    (
        CLE_DELAI_RELANCE_VALIDATION,
        "24",
        "ENTIER",
        "Délai avant relance d'un mouvement sans décision (heures)",
    ),
    # Valeurs du cahier des charges (RG-S10, RG-S11), lues par le stock (B3).
    ("delai_saisie_retroactive_h", "48", "ENTIER", "Délai de saisie rétroactive (heures)"),
    ("derive_horloge_max_min", "5", "ENTIER", "Dérive d'horloge tolérée (minutes)"),
]


def _statut_logement(rang: int) -> str:
    """Même avancement que la simulation du web : 0 étape validée → à venir,
    10 → livré, entre les deux → en cours."""
    etapes_validees = (rang * 7) % 11
    if etapes_validees == 0:
        return STATUT_LOGEMENT_A_VENIR
    if etapes_validees == 10:
        return STATUT_LOGEMENT_LIVRE
    return STATUT_LOGEMENT_EN_COURS


def charger(mot_de_passe: str) -> dict[str, int]:
    """Crée ou met à jour l'organisation du pilote (rejouable)."""
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
    types = {}
    for code, libelle in TYPES_LOGEMENT:
        types[code], _ = TypeLogement.objects.update_or_create(
            code_type=code, defaults={"libelle": libelle, "actif": True}
        )
    zones = []
    for code, nom in ZONES:
        zone, _ = Zone.objects.update_or_create(
            id_zone=uid("zone", code),
            defaults={
                "code": code,
                "nom": nom,
                "type_zone": TYPE_ZONE_TRANCHE,
                "chantier": chantier,
            },
        )
        zones.append(zone)
    # Douze logements répartis sur les trois îlots : A01, B01, C01, A02…
    codes_types = [code for code, _libelle in TYPES_LOGEMENT]
    for rang in range(12):
        numero = f"{ZONES[rang % 3][0]}{rang // 3 + 1:02d}"
        Logement.objects.update_or_create(
            id_logement=uid("logement", numero),
            defaults={
                "numero": numero,
                "statut": _statut_logement(rang),
                "zone": zones[rang % 3],
                "type_logement": types[codes_types[rang % 3]],
            },
        )
    for cle, valeur, type_valeur, libelle in PARAMETRES:
        ParametreChantier.objects.update_or_create(
            id_parametre=uid("parametre", cle),
            defaults={
                "cle": cle,
                "valeur": valeur,
                "type_valeur": type_valeur,
                "libelle": libelle,
                "chantier": chantier,
            },
        )
    return {
        "chantier": 1,
        "magasin": 1,
        "types de logement": len(TYPES_LOGEMENT),
        "zones": len(ZONES),
        "logements": 12,
        "paramètres": len(PARAMETRES),
    }
