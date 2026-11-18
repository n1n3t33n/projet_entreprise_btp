"""Valeurs énumérées et codes du domaine identité.

Arbitrage Q8 (2026-11-18) : ces listes FIGENT le schéma du domaine identité.
Elles sont toutes définies ICI et nulle part ailleurs ; les contraintes CHECK
sont construites à partir de ces tuples (MPD § 6.5 : varchar + CHECK
remplaçable, jamais un ENUM natif).

Les RÔLES et PERMISSIONS, eux, ne sont PAS des énumérations : ce sont des
tables (« données en base et non du code », MPD § 6.5). Les codes de rôle
ci-dessous ne servent qu'à la migration de données initiale et aux données de
démonstration ; aucune logique ne teste « si rôle == … ».
"""

# --- utilisateur.statut (ck_utilisateur_statut) -----------------------------
STATUT_UTILISATEUR_ACTIF = "ACTIF"
STATUT_UTILISATEUR_INACTIF = "INACTIF"
STATUTS_UTILISATEUR: tuple[str, ...] = (STATUT_UTILISATEUR_ACTIF, STATUT_UTILISATEUR_INACTIF)

# --- appareil.statut (ck_appareil_statut) -----------------------------------
# REVOQUE : DÉDUCTION d'ET-4 (« Appareil révoqué ») et de CL-1
# ``Appareil.revoquer()`` ; le CHECK du MPD-1 se termine par « … » et le
# cahier des charges ne le confirme pas (incohérence I-10, arbitrage Q8).
STATUT_APPAREIL_ACTIF = "ACTIF"
STATUT_APPAREIL_REVOQUE = "REVOQUE"
STATUT_APPAREIL_INACTIF = "INACTIF"
STATUTS_APPAREIL: tuple[str, ...] = (
    STATUT_APPAREIL_ACTIF,
    STATUT_APPAREIL_REVOQUE,
    STATUT_APPAREIL_INACTIF,
)

# --- permission.action (ck_permission_action) -------------------------------
# LIRE et non CONSULTER : décision du 2026-11-09, alignée sur MPD-1 et CL-1.
ACTION_LIRE = "LIRE"
ACTION_CREER = "CREER"
ACTION_MODIFIER = "MODIFIER"
ACTION_VALIDER = "VALIDER"
ACTIONS_PERMISSION: tuple[str, ...] = (ACTION_LIRE, ACTION_CREER, ACTION_MODIFIER, ACTION_VALIDER)

# --- droit_accorde.portee (ck_droit_accorde_portee) -------------------------
# Arbitrage Q8 : {GLOBALE, PERIMETRE} pour l'instant, parce que ``perimetre``
# ne relie aujourd'hui qu'un chantier et un magasin (I-20). La liste est
# volontairement EXTENSIBLE : ajouter CHANTIER, ZONE ou LOGEMENT en v0.2 ne
# demandera qu'une valeur ici, une migration de contrainte, les liens de table
# manquants et un « résolveur de portée » (services/droits.py). Aucune logique
# ne suppose que ces deux valeurs sont les seules possibles.
PORTEE_GLOBALE = "GLOBALE"
PORTEE_PERIMETRE = "PERIMETRE"
PORTEES_DROIT: tuple[str, ...] = (PORTEE_GLOBALE, PORTEE_PERIMETRE)

# --- Modules de permission (colonne permission.module) ----------------------
MODULE_API = "api"  # ressources de l'API (EF-AUT-07 : contrôle à chaque requête)
MODULE_ECRAN = "ecran"  # écrans du poste de pilotage web
MODULE_MOBILE = "mobile"  # onglets de l'application mobile (lève I-06)
MODULE_TECHNIQUE = "technique"  # administration Django, documentation d'API

# --- Codes de rôle (arbitrage Q8 : UPPER_SNAKE, 9 rôles) ---------------------
ROLE_DIRECTION = "DIRECTION"
ROLE_ADMINISTRATEUR = "ADMINISTRATEUR"
ROLE_COMMERCIAL = "COMMERCIAL"
ROLE_RESPONSABLE_TECHNIQUE = "RESPONSABLE_TECHNIQUE"
ROLE_ACQUEREUR = "ACQUEREUR"
ROLE_MAGASINIER = "MAGASINIER"
ROLE_TECHNICIEN = "TECHNICIEN"
ROLE_CHEF_CHANTIER = "CHEF_CHANTIER"
ROLE_GESTIONNAIRE_STOCK = "GESTIONNAIRE_STOCK"

# --- Actions inscrites au journal d'audit (RG-D9) ---------------------------
# Libellés destinés à l'écran « Journal d'audit » : phrases simples, sans code.
AUDIT_CONNEXION = "CONNEXION"
AUDIT_ECHEC_CONNEXION = "ECHEC_CONNEXION"
AUDIT_DECONNEXION = "DECONNEXION"
AUDIT_ENROLEMENT_APPAREIL = "ENROLEMENT_APPAREIL"
AUDIT_REVOCATION_APPAREIL = "REVOCATION_APPAREIL"
AUDIT_CREATION_COMPTE = "CREATION_COMPTE"
AUDIT_MODIFICATION_COMPTE = "MODIFICATION_COMPTE"
AUDIT_DESACTIVATION_COMPTE = "DESACTIVATION_COMPTE"
AUDIT_MODIFICATION_DROITS = "MODIFICATION_DROITS"

LIBELLES_AUDIT: dict[str, str] = {
    AUDIT_CONNEXION: "Connexion",
    AUDIT_ECHEC_CONNEXION: "Échec de connexion",
    AUDIT_DECONNEXION: "Déconnexion",
    AUDIT_ENROLEMENT_APPAREIL: "Enrôlement d'un appareil",
    AUDIT_REVOCATION_APPAREIL: "Révocation d'un appareil",
    AUDIT_CREATION_COMPTE: "Création d'un compte",
    AUDIT_MODIFICATION_COMPTE: "Modification d'un compte",
    AUDIT_DESACTIVATION_COMPTE: "Désactivation d'un compte",
    AUDIT_MODIFICATION_DROITS: "Modification de la matrice des droits",
}

# Types d'objet audités (colonne journal_audit.type_objet).
OBJET_UTILISATEUR = "utilisateur"
OBJET_APPAREIL = "appareil"
OBJET_DROITS = "droit_accorde"
