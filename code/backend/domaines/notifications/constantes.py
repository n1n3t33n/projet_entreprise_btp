"""Valeurs fermées et catalogue initial des notifications (MPD-5, EF-NOT-01).

Les CHECK de canal du MPD-5 se terminent par « … » (I-12) : domaine arbitré
le 2026-11-23 (Q-AR). Seul le canal APPLICATION est produit pour le pilote ;
PUSH (EF-NOT-02, priorité C) et COURRIEL restent permis par le schéma.
"""

# --- Canaux (Q-AR) ---------------------------------------------------------------------
APPLICATION = "APPLICATION"
PUSH = "PUSH"
COURRIEL = "COURRIEL"
CANAUX: tuple[str, ...] = (APPLICATION, PUSH, COURRIEL)

# --- Types de notification (Q-AP) ---------------------------------------------------------
# Les {champs} des modèles de message viennent du contexte publié par le
# domaine émetteur (socle/evenements.py) ; un champ absent reste vide.
SORTIE_A_VALIDER = "SORTIE_A_VALIDER"
VALIDATION_EN_RETARD = "VALIDATION_EN_RETARD"
SORTIE_REFUSEE = "SORTIE_REFUSEE"
SEUIL_MINIMAL = "SEUIL_MINIMAL"
SEUIL_CRITIQUE = "SEUIL_CRITIQUE"
STOCK_NEGATIF = "STOCK_NEGATIF"
ETAPE_A_CONTROLER = "ETAPE_A_CONTROLER"
ETAPE_REJETEE = "ETAPE_REJETEE"
ETAPE_BLOQUEE = "ETAPE_BLOQUEE"
MANQUE_MATERIEL = "MANQUE_MATERIEL"
ETAPE_EN_RETARD = "ETAPE_EN_RETARD"
ANOMALIE_SYNCHRONISATION = "ANOMALIE_SYNCHRONISATION"
RAPPORT_HEBDOMADAIRE = "RAPPORT_HEBDOMADAIRE"

# Le catalogue (libellés, modèles de message) et les abonnements par défaut
# sont des DONNÉES, posées par la migration notifications 0002 et réglables
# ensuite dans l'administration (Q5).
