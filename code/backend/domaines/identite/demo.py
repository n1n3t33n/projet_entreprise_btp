"""Jeu de démonstration « identité » du chantier pilote de Grand-Bassam.

Identique à celui des deux fronts (rapport B0 § 3.6) : les comptes du web
(``lib/mocks/auth-grand-bassam.ts``), ceux du mobile (``ServiceAuthSimule``),
les équipes du web (``equipes-grand-bassam.ts``), les périmètres du pilote et
la matrice initiale des écrans (``droits-grand-bassam.ts``) et des onglets
mobiles (``onglet_role.dart``). Seules différences voulues :
  * codes de rôle en UPPER_SNAKE (arbitrage Q8) ;
  * identifiants techniques en uuid (MPD), stables d'un chargement à l'autre ;
  * mot de passe lu dans DEMO_MOT_DE_PASSE, jamais écrit dans le code.

Écart signalé (I-20) : le web rattache l'acquéreuse au périmètre « Logement
A01 », que le MPD ne sait pas représenter ; elle reçoit le chantier.

Rejouable : chaque chargement met à jour au lieu de dupliquer.
"""

from datetime import date, datetime
from typing import Any

from django.db import transaction
from django.utils import timezone

from domaines.identite.constantes import PORTEE_GLOBALE
from domaines.identite.models import (
    AffectationRole,
    DroitAccorde,
    Equipe,
    MembreEquipe,
    Perimetre,
    Utilisateur,
)
from domaines.organisation import demo as demo_organisation
from domaines.organisation import selecteurs as selecteurs_organisation
from socle.demo import uid

# (identifiant, prénom, nom, fonction, rôle, périmètre, date de création)
COMPTES = [
    # Poste de pilotage web
    (
        "a.kouassi",
        "Affoué",
        "Kouassi",
        "Associée, direction générale",
        "DIRECTION",
        "programme",
        date(2026, 9, 1),
    ),
    (
        "y.bamba",
        "Yacouba",
        "Bamba",
        "Administrateur du système",
        "ADMINISTRATEUR",
        "programme",
        date(2026, 9, 1),
    ),
    (
        "k.n-guessan",
        "Koffi",
        "N'Guessan",
        "Conducteur de travaux",
        "RESPONSABLE_TECHNIQUE",
        "chantier",
        date(2026, 9, 5),
    ),
    (
        "s.traore",
        "Salimata",
        "Traoré",
        "Chargée de clientèle",
        "COMMERCIAL",
        "chantier",
        date(2026, 9, 12),
    ),
    ("m.diallo", "Mariam", "Diallo", "Acquéreuse", "ACQUEREUR", "chantier", date(2026, 10, 2)),
    # Application mobile de terrain
    ("magasinier", "Mamadou", "Koné", "Magasinier", "MAGASINIER", "magasin", date(2026, 9, 1)),
    (
        "technicien",
        "Kouassi",
        "Adama",
        "Chef d'équipe maçonnerie",
        "TECHNICIEN",
        "chantier",
        date(2026, 9, 1),
    ),
    (
        "chef",
        "Mamadou",
        "Traoré",
        "Chef de chantier",
        "CHEF_CHANTIER",
        "chantier",
        date(2026, 9, 1),
    ),
    (
        "gestionnaire",
        "Idriss",
        "Sékou",
        "Gestionnaire de stock",
        "GESTIONNAIRE_STOCK",
        "magasin",
        date(2026, 9, 1),
    ),
    (
        "responsable",
        "Awa",
        "Bamba",
        "Responsable technique",
        "RESPONSABLE_TECHNIQUE",
        "chantier",
        date(2026, 9, 1),
    ),
]

# Membres d'équipe du web sans accès à l'application (aucun rôle, aucun mot
# de passe utilisable) : ils existent comme personnes, pas comme comptes.
MEMBRES_SANS_ACCES = [
    ("a.kone", "Adama", "Koné", "Maçon", date(2026, 9, 10)),
    ("i.ouattara", "Issa", "Ouattara", "Ferrailleur", date(2026, 9, 10)),
    ("f.sanogo", "Fatou", "Sanogo", "Cheffe de chantier", date(2026, 9, 15)),
    ("b.cisse", "Bakary", "Cissé", "Carreleur", date(2026, 9, 20)),
]

# (code, libellé, [(identifiant, chef ?, date de début)])
EQUIPES = [
    (
        "GO-A",
        "Gros œuvre — équipe A",
        [
            ("k.n-guessan", True, date(2026, 9, 5)),
            ("a.kone", False, date(2026, 9, 10)),
            ("i.ouattara", False, date(2026, 9, 10)),
        ],
    ),
    (
        "SO-B",
        "Second œuvre — équipe B",
        [("f.sanogo", True, date(2026, 9, 15)), ("b.cisse", False, date(2026, 9, 20))],
    ),
]

# Matrice initiale du web (droits-grand-bassam.ts), codes de rôle en UPPER_SNAKE.
ECRANS_PAR_ROLE = {
    "DIRECTION": ["tableau-de-bord", "avancement", "journal", "stock"],
    "ADMINISTRATEUR": ["referentiels", "parametrage", "administration", "synchronisation"],
    "COMMERCIAL": ["avancement"],
    "RESPONSABLE_TECHNIQUE": [
        "tableau-de-bord",
        "avancement",
        "journal",
        "stock",
        "referentiels",
        "gammes",
        "equipes",
        "parametrage",
        "synchronisation",
    ],
    "ACQUEREUR": ["espace-acquereur"],
}

# Onglets mobiles (onglet_role.dart, ``ongletsPour``), dans l'ordre affiché.
ONGLETS_PAR_ROLE = {
    "MAGASINIER": ["stock", "historique", "synchro", "profil"],
    "GESTIONNAIRE_STOCK": ["stock", "a-valider", "historique", "profil"],
    "TECHNICIEN": ["fiches", "historique", "synchro", "profil"],
    "CHEF_CHANTIER": ["a-valider", "fiches", "stock", "profil"],
    "RESPONSABLE_TECHNIQUE": ["a-valider", "fiches", "profil"],
}

# Lecture des référentiels (B2) : tous les rôles internes et de terrain ;
# l'acquéreur n'en a pas besoin (il ne voit que son espace).
LECTURE_REFERENTIELS = [
    f"api.{ressource}.lire"
    for ressource in (
        "chantiers",
        "magasins",
        "logements",
        "types-logement",
        "parametres",
        "articles",
        "categories",
        "unites",
        "corps-etat",
        "gammes",
        "types-mouvement",
        "motifs-blocage",
        "regles",
    )
]
ROLES_LECTEURS_REFERENTIELS = [
    "DIRECTION",
    "COMMERCIAL",
    "RESPONSABLE_TECHNIQUE",
    "MAGASINIER",
    "TECHNICIEN",
    "CHEF_CHANTIER",
    "GESTIONNAIRE_STOCK",
]

# Droits d'écriture métier (l'administrateur a déjà tout par amorçage) :
# EF-AUT-08 — journal d'audit consultable aussi par la direction ;
# gammes, corps d'état, paramètres et règles — responsable technique (EF-REF-05,
# 07 à 09) ; catalogue et magasins — gestionnaire de stock (EF-REF-03, 04).
# Synchronisation (B5) : tout rôle de terrain envoie ses lots depuis le mobile.
# Le gestionnaire de stock traite les anomalies de synchronisation (EF-SYN-05).
DROITS_API_SUPPLEMENTAIRES = {
    "DIRECTION": ["api.audit.lire", "api.stock.lire", "api.mouvements.lire", "api.avancement.lire"],
    "COMMERCIAL": ["api.avancement.lire"],
    # Stock (B3) : saisie et comptage au magasinier, décisions au gestionnaire
    # (RG-D8 : celui qui saisit ne valide pas), lecture aux rôles de pilotage.
    "MAGASINIER": [
        "api.stock.lire",
        "api.mouvements.lire",
        "api.mouvements.creer",
        "api.inventaires.lire",
        "api.inventaires.creer",
        "api.inventaires.modifier",
        "api.synchronisation.creer",
    ],
    # Avancement (B4) : le technicien déclare et lit ses fiches ; chef de
    # chantier et responsable technique affectent, contrôlent (RG-A4) et
    # clôturent ; RG-D11 empêche de contrôler sa propre déclaration.
    "CHEF_CHANTIER": [
        "api.stock.lire",
        "api.mouvements.lire",
        "api.avancement.lire",
        "api.etapes.modifier",
        "api.etapes.valider",
        "api.fiches-route.lire",
        "api.fiches-route.creer",
        "api.fiches-route.modifier",
        "api.synchronisation.creer",
    ],
    "TECHNICIEN": [
        "api.stock.lire",
        "api.avancement.lire",
        "api.etapes.modifier",
        "api.fiches-route.lire",
        "api.synchronisation.creer",
    ],
    "RESPONSABLE_TECHNIQUE": [
        "api.stock.lire",
        "api.mouvements.lire",
        "api.avancement.lire",
        "api.etapes.modifier",
        "api.etapes.valider",
        "api.fiches-route.lire",
        "api.fiches-route.creer",
        "api.fiches-route.modifier",
        "api.corps-etat.creer",
        "api.corps-etat.modifier",
        "api.gammes.creer",
        "api.gammes.modifier",
        "api.gammes.valider",
        "api.parametres.creer",
        "api.parametres.modifier",
        "api.regles.creer",
        "api.regles.modifier",
        "api.synchronisation.creer",
    ],
    "GESTIONNAIRE_STOCK": [
        "api.stock.lire",
        "api.mouvements.lire",
        "api.mouvements.creer",
        "api.mouvements.valider",
        "api.seuils.modifier",
        "api.inventaires.lire",
        "api.inventaires.creer",
        "api.inventaires.modifier",
        "api.inventaires.valider",
        "api.articles.creer",
        "api.articles.modifier",
        "api.magasins.creer",
        "api.magasins.modifier",
        "api.import.creer",
        "api.synchronisation.creer",
        "api.anomalies.lire",
        "api.anomalies.modifier",
    ],
}


def _horodatage(jour: date) -> datetime:
    return timezone.make_aware(datetime(jour.year, jour.month, jour.day, 8, 0))


def _perimetres() -> dict[str, Perimetre]:
    """Périmètres du pilote. Le chantier et le magasin appartiennent au
    domaine « organisation », chargé avant celui-ci : on les LIT par ses
    sélecteurs, on ne les crée jamais ici (règle de modularité)."""
    chantier = selecteurs_organisation.chantier_par_code(demo_organisation.CODE_CHANTIER)
    magasin = selecteurs_organisation.magasin_par_code(demo_organisation.CODE_MAGASIN)
    if chantier is None or magasin is None:
        raise LookupError(
            "Le chantier et le magasin de démonstration doivent être chargés d'abord."
        )
    perimetres: dict[str, Perimetre] = {}
    definitions: list[tuple[str, str, dict[str, Any]]] = [
        ("programme", "Tout le programme", {"chantier": None, "magasin": None}),
        ("chantier", "Chantier de Grand-Bassam", {"chantier": chantier, "magasin": None}),
        ("magasin", "Magasin central de Grand-Bassam", {"chantier": None, "magasin": magasin}),
    ]
    for cle, libelle, valeurs in definitions:
        perimetres[cle], _ = Perimetre.objects.update_or_create(
            id_perimetre=uid("perimetre", cle), defaults={"libelle": libelle, **valeurs}
        )
    return perimetres


def _utilisateur(
    identifiant: str, prenom: str, nom: str, fonction: str, cree: date, mot_de_passe: str | None
) -> Utilisateur:
    utilisateur, _ = Utilisateur.objects.update_or_create(
        id_utilisateur=uid("utilisateur", identifiant),
        defaults={
            "identifiant": identifiant,
            "prenom": prenom,
            "nom": nom,
            "fonction": fonction,
            "statut": "ACTIF",
            "date_creation": _horodatage(cree),
        },
    )
    if mot_de_passe:
        utilisateur.set_password(mot_de_passe)
    else:
        utilisateur.set_unusable_password()
    utilisateur.save(update_fields=["password"])
    return utilisateur


def _matrice() -> None:
    """Remplace la matrice « ecran » et « mobile » par celle des fronts ; les
    droits d'amorçage (« api », « technique ») de la migration restent."""
    DroitAccorde.objects.filter(permission__module__in=["ecran", "mobile"]).delete()
    lignes: list[tuple[str, str]] = []
    for role, ecrans in ECRANS_PAR_ROLE.items():
        lignes += [(role, f"ecran.{ecran}.lire") for ecran in ecrans]
    for role, onglets in ONGLETS_PAR_ROLE.items():
        lignes += [(role, f"mobile.{onglet}.lire") for onglet in onglets]
    for role in ROLES_LECTEURS_REFERENTIELS:
        lignes += [(role, permission) for permission in LECTURE_REFERENTIELS]
    for role, permissions in DROITS_API_SUPPLEMENTAIRES.items():
        lignes += [(role, permission) for permission in permissions]
    for role, permission in lignes:
        DroitAccorde.objects.update_or_create(
            role_id=role, permission_id=permission, defaults={"portee": PORTEE_GLOBALE}
        )


@transaction.atomic
def charger(mot_de_passe: str) -> dict[str, int]:
    """Charge (ou recharge) tout le jeu identité. Rend un petit bilan."""
    perimetres = _perimetres()
    for identifiant, prenom, nom, fonction, role, perimetre, cree in COMPTES:
        utilisateur = _utilisateur(identifiant, prenom, nom, fonction, cree, mot_de_passe)
        AffectationRole.objects.update_or_create(
            role_id=role,
            perimetre=perimetres[perimetre],
            utilisateur=utilisateur,
            defaults={"date_debut": cree, "date_fin": None},
        )
    for identifiant, prenom, nom, fonction, cree in MEMBRES_SANS_ACCES:
        _utilisateur(identifiant, prenom, nom, fonction, cree, None)
    for code, libelle, membres in EQUIPES:
        equipe, _ = Equipe.objects.update_or_create(
            id_equipe=uid("equipe", code),
            defaults={"code": code, "libelle": libelle, "actif": True},
        )
        for identifiant, chef, debut in membres:
            MembreEquipe.objects.update_or_create(
                utilisateur_id=uid("utilisateur", identifiant),
                equipe=equipe,
                defaults={"est_chef_equipe": chef, "date_debut": debut, "date_fin": None},
            )
    _matrice()
    return {
        "comptes": len(COMPTES),
        "membres sans accès": len(MEMBRES_SANS_ACCES),
        "équipes": len(EQUIPES),
        "périmètres": len(perimetres),
    }
