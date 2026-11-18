"""Valeurs énumérées du domaine « référentiels et catalogue » (MPD-3).

Les colonnes contraintes par un CHECK au MPD-3 reçoivent leur CHECK, construit
depuis ces tuples (domaines arbitrés le 2026-11-18, Q-A). Les colonnes que le
MPD laisse VOLONTAIREMENT libres (``regle_validation.type_evenement`` et
``operateur``, varchar(120) sans CHECK) ne reçoivent aucune contrainte en
base : leurs valeurs admises sont listées ici et contrôlées par l'API, sans
créer d'écart au modèle.
"""

# unite_mesure.type_unite — ck_unite_mesure_type_unite. UNITE (sac, barre)
# et SURFACE (m²) complètent les trois valeurs écrites au MPD.
TYPES_UNITE: tuple[str, ...] = ("MASSE", "VOLUME", "LONGUEUR", "UNITE", "SURFACE")

# article.origine — ck_article_origine (valeurs écrites au MPD-3).
ORIGINES_ARTICLE: tuple[str, ...] = ("ACHAT", "PRODUCTION_INTERNE", "RECUPERATION")

# gamme.statut — ck_gamme_statut. Cycle d'une version de gamme (EF-REF-09) :
# un brouillon se publie (ACTIVE) ; l'ancienne version active du même type de
# logement passe ARCHIVEE.
STATUT_GAMME_BROUILLON = "BROUILLON"
STATUT_GAMME_ACTIVE = "ACTIVE"
STATUT_GAMME_ARCHIVEE = "ARCHIVEE"
STATUTS_GAMME: tuple[str, ...] = (
    STATUT_GAMME_BROUILLON,
    STATUT_GAMME_ACTIVE,
    STATUT_GAMME_ARCHIVEE,
)

# regle_validation.type_evenement et .operateur — SANS CHECK en base (le MPD
# les laisse libres) ; contrôlés par l'API (EF-REF-08).
TYPES_EVENEMENT_REGLE: tuple[str, ...] = (
    "DECLARATION_ETAPE",
    "VALIDATION_ETAPE",
    "ECART_INVENTAIRE",
    "MOUVEMENT_STOCK",
)
OPERATEURS_REGLE: tuple[str, ...] = (
    "INFERIEUR_EGAL",
    "SUPERIEUR_EGAL",
    "EGAL",
    "INFERIEUR",
    "SUPERIEUR",
)
