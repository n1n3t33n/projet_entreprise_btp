"""Valeurs des listes fermées du domaine « stock » (MPD-4).

Les CHECK du MPD-4 se terminent par « … » (I-12) ; les domaines ci-dessous
ont été arbitrés le 2026-11-22 (Q-J). Ils sont posés en base par des
contraintes CHECK remplaçables, jamais par un type ENUM.
"""

# --- mouvement_stock.statut_validation (Q-J, Q-K) --------------------------
# Écrit UNE fois, à l'insertion : ENREGISTRE (aucune règle applicable) ou
# A_VALIDER (une règle de validation s'est déclenchée, RG-S6). Le statut servi
# par l'API est DÉRIVÉ des événements (ET-2) : voir STATUTS_DERIVES.
STATUT_ENREGISTRE = "ENREGISTRE"
STATUT_A_VALIDER = "A_VALIDER"
STATUTS_VALIDATION: tuple[str, ...] = (STATUT_ENREGISTRE, STATUT_A_VALIDER)

# Statuts dérivés (ET-2), servis par l'API et attendus par le web.
STATUT_VALIDE = "VALIDE"
STATUT_EN_ALERTE = "EN_ALERTE"
STATUT_REJETE = "REJETE"
STATUT_ANNULE = "ANNULE"
STATUTS_DERIVES: tuple[str, ...] = (
    STATUT_ENREGISTRE,
    STATUT_A_VALIDER,
    STATUT_EN_ALERTE,
    STATUT_VALIDE,
    STATUT_REJETE,
    STATUT_ANNULE,
)

# --- evenement_validation.decision ------------------------------------------
DECISION_ACCEPTE = "ACCEPTE"
DECISION_REFUSE = "REFUSE"
DECISIONS: tuple[str, ...] = (DECISION_ACCEPTE, DECISION_REFUSE)

# Valeur de evenement_validation.type_objet pour la décision sur un mouvement.
OBJET_MOUVEMENT = "mouvement_stock"

# --- niveaux de stock (stock_courant.niveau_alerte, alerte.niveau) ----------
# VIDE ajouté au « … » du MPD : stock nul ou négatif (RG-S7), affiché par le web.
NIVEAU_NORMAL = "NORMAL"
NIVEAU_MINIMAL = "MINIMAL"
NIVEAU_CRITIQUE = "CRITIQUE"
NIVEAU_VIDE = "VIDE"
NIVEAUX: tuple[str, ...] = (NIVEAU_NORMAL, NIVEAU_MINIMAL, NIVEAU_CRITIQUE, NIVEAU_VIDE)

# --- alerte ------------------------------------------------------------------
ALERTE_SEUIL_MINIMAL = "SEUIL_MINIMAL"
ALERTE_SEUIL_CRITIQUE = "SEUIL_CRITIQUE"
ALERTE_STOCK_NEGATIF = "STOCK_NEGATIF"
# Mouvement resté sans décision au-delà du délai de relance (ET-2, Q-P).
ALERTE_VALIDATION_EN_RETARD = "VALIDATION_EN_RETARD"
TYPES_ALERTE: tuple[str, ...] = (
    ALERTE_SEUIL_MINIMAL,
    ALERTE_SEUIL_CRITIQUE,
    ALERTE_STOCK_NEGATIF,
    ALERTE_VALIDATION_EN_RETARD,
)

ALERTE_OUVERTE = "OUVERTE"
ALERTE_TRAITEE = "TRAITEE"
STATUTS_ALERTE: tuple[str, ...] = (ALERTE_OUVERTE, ALERTE_TRAITEE)

# --- inventaire (SQ-4) -------------------------------------------------------
INVENTAIRE_EN_COURS = "EN_COURS"
INVENTAIRE_A_VALIDER = "A_VALIDER"
INVENTAIRE_VALIDE = "VALIDE"
STATUTS_INVENTAIRE: tuple[str, ...] = (INVENTAIRE_EN_COURS, INVENTAIRE_A_VALIDER, INVENTAIRE_VALIDE)

LIGNE_A_COMPTER = "A_COMPTER"
LIGNE_COMPTEE = "COMPTEE"
LIGNE_VALIDEE = "VALIDEE"
STATUTS_LIGNE: tuple[str, ...] = (LIGNE_A_COMPTER, LIGNE_COMPTEE, LIGNE_VALIDEE)

# --- types de mouvement dont le code dépend ----------------------------------
# Ce sont des DONNÉES (table type_mouvement, MPD-3) ; ces quelques codes sont
# créés par la migration de données stock 0003 parce que le serveur les
# emploie lui-même : ajustement d'inventaire (Q-Q), contre-mouvement
# (RG-S8, EF-STK-11), stock de départ importé (EF-ADM-02).
TYPE_AJUSTEMENT_PLUS = "AJU_INVENTAIRE_PLUS"
TYPE_AJUSTEMENT_MOINS = "AJU_INVENTAIRE_MOINS"
TYPE_ANNULATION_PLUS = "ANN_PLUS"
TYPE_ANNULATION_MOINS = "ANN_MOINS"
TYPE_STOCK_INITIAL = "ENT_STOCK_INITIAL"

# --- paramètres de chantier lus par le domaine (Q-R, Q-F) --------------------
CLE_DELAI_SAISIE_RETROACTIVE = "delai_saisie_retroactive_h"  # RG-S10, 48 h
CLE_DERIVE_HORLOGE_MAX = "derive_horloge_max_min"  # RG-S11, 5 min
CLE_STOCK_NEGATIF = "autoriser_stock_negatif"  # RG-S7, vrai par défaut
# Valeurs du cahier des charges, employées si le paramètre manque (avec
# alerte technique PARAMETRE_MANQUANT, comme pour la relance).
DEFAUT_DELAI_SAISIE_RETROACTIVE_H = 48
DEFAUT_DERIVE_HORLOGE_MAX_MIN = 5

# Événement des règles de validation qui concernent le stock (MPD-3).
EVENEMENT_MOUVEMENT = "MOUVEMENT_STOCK"
EVENEMENT_ECART_INVENTAIRE = "ECART_INVENTAIRE"
