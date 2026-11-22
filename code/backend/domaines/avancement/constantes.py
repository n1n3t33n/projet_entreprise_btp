"""Valeurs des listes fermées du domaine « avancement » (MPD-5).

Les CHECK du MPD-5 se terminent par « … » (I-12) ; les domaines ci-dessous
ont été arbitrés le 2026-11-22 (Q-T). Ils sont posés en base par des
contraintes CHECK remplaçables, jamais par un type ENUM.
"""

# --- etape_travaux.statut, evenement_execution.statut_avant/apres (RG-A2, ET-1)
A_FAIRE = "A_FAIRE"
EN_COURS = "EN_COURS"
TERMINEE_DECLAREE = "TERMINEE_DECLAREE"
BLOQUEE = "BLOQUEE"
VALIDEE = "VALIDEE"
STATUTS_ETAPE: tuple[str, ...] = (A_FAIRE, EN_COURS, TERMINEE_DECLAREE, BLOQUEE, VALIDEE)
# Une étape « terminée » au sens de RG-A6 et RG-A8 : déclarée ou validée.
STATUTS_TERMINES: tuple[str, ...] = (TERMINEE_DECLAREE, VALIDEE)

# --- fiche_route (RG-A7, H9) --------------------------------------------------
CYCLE_JOUR = "JOUR"
CYCLE_SEMAINE = "SEMAINE"
CYCLE_QUINZAINE = "QUINZAINE"
CYCLE_LOGEMENT = "LOGEMENT"  # ajouté au « … » du MPD : H9 cite le logement
TYPES_CYCLE: tuple[str, ...] = (CYCLE_JOUR, CYCLE_SEMAINE, CYCLE_QUINZAINE, CYCLE_LOGEMENT)

FICHE_OUVERTE = "OUVERTE"
FICHE_CLOTUREE = "CLOTUREE"
STATUTS_FICHE: tuple[str, ...] = (FICHE_OUVERTE, FICHE_CLOTUREE)

# --- avancement_agrege.portee (RG-A6) -----------------------------------------
PORTEE_CHANTIER = "CHANTIER"
PORTEE_ZONE = "ZONE"
PORTEE_LOGEMENT = "LOGEMENT"
PORTEE_CORPS_ETAT = "CORPS_ETAT"  # ajouté au « … » du MPD : RG-A6, web
PORTEES: tuple[str, ...] = (PORTEE_CHANTIER, PORTEE_ZONE, PORTEE_LOGEMENT, PORTEE_CORPS_ETAT)

# --- paramètre de chantier lu par le domaine (Q-Z) -----------------------------
CLE_TYPE_CYCLE = "type_cycle_fiche_route"
# Valeur de démonstration, à confirmer avec Italia (H9) ; employée avec une
# alerte technique PARAMETRE_MANQUANT si le paramètre manque.
DEFAUT_TYPE_CYCLE = CYCLE_SEMAINE

# --- libellés d'événements (commentaire, varchar(120) au MPD) -------------------
LONGUEUR_COMMENTAIRE = 120
MOTIF_REPORT_FIN_DE_CYCLE = "Non faite en fin de cycle"
COMMENTAIRE_VALIDATION_IMPLICITE = "Validation implicite : étape sans contrôle (RG-A4)"
