"""Valeurs des listes fermées du domaine « synchronisation » (MPD-6).

Les CHECK du MPD-6 se terminent par « … » (I-12) ; les domaines ci-dessous
ont été arbitrés le 2026-11-23 (Q-AJ, Q-AM). CHECK remplaçables, jamais ENUM.
"""

# --- resultat_evenement.statut (Q-AM, ET-3) ------------------------------------
# « En attente » et « en cours » sont des états du téléphone (file d'envoi) ;
# le serveur ne rend que l'issue du traitement.
ACCEPTE = "ACCEPTE"
DEJA_RECU = "DEJA_RECU"
REJETE = "REJETE"
STATUTS_RESULTAT: tuple[str, ...] = (ACCEPTE, DEJA_RECU, REJETE)

# --- anomalie_synchronisation (Q-AJ, EF-SYN-05) ---------------------------------
ECART_QUANTITE = "ECART_QUANTITE"  # stock devenu négatif (RG-S7)
CONFLIT_VERSION = "CONFLIT_VERSION"  # l'objet a changé sur le serveur entre-temps
REJET_REGLE = "REJET_REGLE"  # événement refusé par une règle métier
DERIVE_HORLOGE = "DERIVE_HORLOGE"  # horloge de l'appareil décalée (RG-S11)
TYPES_ANOMALIE: tuple[str, ...] = (ECART_QUANTITE, CONFLIT_VERSION, REJET_REGLE, DERIVE_HORLOGE)

ANOMALIE_OUVERTE = "OUVERTE"
ANOMALIE_TRAITEE = "TRAITEE"
STATUTS_ANOMALIE: tuple[str, ...] = (ANOMALIE_OUVERTE, ANOMALIE_TRAITEE)

# Motifs de rejet qui traduisent un état changé sur le serveur depuis la saisie
# hors ligne : l'anomalie est un conflit, pas une faute de saisie.
MOTIFS_CONFLIT: frozenset[str] = frozenset(
    {
        "DECISION_IMPOSSIBLE",
        "TRANSITION_IMPOSSIBLE",
        "UUID_DEJA_UTILISE",
        "DEJA_ANNULE",
        "ETAPE_TERMINEE",
        "INTROUVABLE",
    }
)

# --- garde-fous (Q-AL) ------------------------------------------------------------
EVENEMENTS_PAR_LOT_MAX = 200
TAILLE_DECOMPRESSEE_MAX = 5_000_000  # octets : protège contre une « bombe gzip »
# RG-S11 : dérive tolérée entre l'heure d'envoi déclarée par l'appareil et
# celle du serveur (valeur du cahier des charges).
DERIVE_HORLOGE_MAX_MIN = 5
