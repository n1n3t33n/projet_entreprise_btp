"""Valeurs énumérées du domaine « organisation du chantier » (MPD-2).

Chaque énuméré est un varchar(32) assorti d'une contrainte CHECK construite
depuis ces tuples, jamais un type ENUM PostgreSQL (MPD § 6.5 : un CHECK se
remplace, un ENUM impose une migration de type). Ajouter une valeur, c'est
l'ajouter ici puis générer la migration de contrainte.

Les listes du MPD-2 sont tronquées par « … » (I-12) ; celles-ci sont les
domaines arbitrés le 2026-11-18 (B2, Q-A).
"""

# chantier.statut — ck_chantier_statut. OUVERT, valeur du motif générique du
# MPD (I-12), est retirée : un chantier est actif ou ne l'est plus.
STATUT_CHANTIER_ACTIF = "ACTIF"
STATUT_CHANTIER_INACTIF = "INACTIF"
STATUTS_CHANTIER: tuple[str, ...] = (STATUT_CHANTIER_ACTIF, STATUT_CHANTIER_INACTIF)

# zone.type_zone — ck_zone_type_zone (valeurs écrites au MPD-2).
TYPE_ZONE_BATIMENT = "BATIMENT"
TYPE_ZONE_NIVEAU = "NIVEAU"
TYPE_ZONE_TRANCHE = "TRANCHE"
TYPES_ZONE: tuple[str, ...] = (TYPE_ZONE_BATIMENT, TYPE_ZONE_NIVEAU, TYPE_ZONE_TRANCHE)

# logement.statut — ck_logement_statut. Cycle de vie du logement, cohérent
# avec date_livraison_prevue. Le module Référentiels du web emploie encore
# ACTIF/INACTIF pour cette même colonne (I-34) : il s'alignera (F-11).
STATUT_LOGEMENT_A_VENIR = "A_VENIR"
STATUT_LOGEMENT_EN_COURS = "EN_COURS"
STATUT_LOGEMENT_LIVRE = "LIVRE"
STATUTS_LOGEMENT: tuple[str, ...] = (
    STATUT_LOGEMENT_A_VENIR,
    STATUT_LOGEMENT_EN_COURS,
    STATUT_LOGEMENT_LIVRE,
)

# parametre_chantier.type_valeur — ck_parametre_chantier_type_valeur.
# TEXTE complète la liste du MPD (devise, libellés libres).
TYPE_VALEUR_ENTIER = "ENTIER"
TYPE_VALEUR_DECIMAL = "DECIMAL"
TYPE_VALEUR_BOOLEEN = "BOOLEEN"
TYPE_VALEUR_TEXTE = "TEXTE"
TYPES_VALEUR: tuple[str, ...] = (
    TYPE_VALEUR_ENTIER,
    TYPE_VALEUR_DECIMAL,
    TYPE_VALEUR_BOOLEEN,
    TYPE_VALEUR_TEXTE,
)

# Clé du paramètre de chantier qui fixe le délai de relance des mouvements
# sans décision (ET-2, EF-REF-07). Décision Q-F (2026-11-18) : ce paramètre
# l'emporte ; regle_validation.delai_heures ne sert qu'à défaut ; sans aucune
# valeur, pas de relance et alerte technique. Utilisé à partir de B3.
CLE_DELAI_RELANCE_VALIDATION = "delai_relance_validation_h"
