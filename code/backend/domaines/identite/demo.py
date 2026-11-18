"""Jeu de démonstration « identité » du chantier pilote de Grand-Bassam.

Identique à celui des deux fronts (rapport B0 § 3.6) : les comptes du web
(``lib/mocks/auth-grand-bassam.ts``), ceux du mobile (``ServiceAuthSimule``),
les équipes du web (``equipes-grand-bassam.ts``), le magasin « GB-CENTRAL » et
la matrice initiale des écrans (``droits-grand-bassam.ts``) et des onglets
mobiles (``onglet_role.dart``). Seules différences voulues :
  * codes de rôle en UPPER_SNAKE (arbitrage Q8) ;
  * identifiants techniques en uuid (MPD), stables d'un chargement à l'autre ;
  * mot de passe lu dans DEMO_MOT_DE_PASSE, jamais écrit dans le code.

Écart signalé (I-20) : le web rattache l'acquéreuse au périmètre « Logement
A01 », que le MPD ne sait pas représenter ; elle reçoit le chantier.

Rejouable : chaque chargement met à jour au lieu de dupliquer.
"""

import uuid
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
from domaines.organisation.models import Chantier, Magasin

ESPACE = uuid.UUID("6f1c2d3e-4b5a-4c6d-8e7f-0a1b2c3d4e5f")


def uid(nature: str, cle: str) -> uuid.UUID:
    """Identifiant stable : le même à chaque chargement."""
    return uuid.uuid5(ESPACE, f"{nature}:{cle}")


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

# EF-AUT-08 : le journal d'audit se consulte par l'administrateur ET la direction.
DROITS_API_SUPPLEMENTAIRES = {"DIRECTION": ["api.audit.lire"]}


def _horodatage(jour: date) -> datetime:
    return timezone.make_aware(datetime(jour.year, jour.month, jour.day, 8, 0))


def _organisation() -> dict[str, Perimetre]:
    chantier, _ = Chantier.objects.update_or_create(
        id_chantier=uid("chantier", "CH-GB"),
        defaults={
            "code": "CH-GB",
            "nom": "Chantier de Grand-Bassam",
            "programme": "Programme Grand-Bassam — villas et duplex",
            "date_debut": date(2026, 9, 1),
            "statut": "ACTIF",
        },
    )
    magasin, _ = Magasin.objects.update_or_create(
        id_magasin=uid("magasin", "GB-CENTRAL"),
        defaults={
            "code": "GB-CENTRAL",
            "nom": "Magasin central",
            "actif": True,
            "chantier": chantier,
        },
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
    for role, permissions in DROITS_API_SUPPLEMENTAIRES.items():
        lignes += [(role, permission) for permission in permissions]
    for role, permission in lignes:
        DroitAccorde.objects.update_or_create(
            role_id=role, permission_id=permission, defaults={"portee": PORTEE_GLOBALE}
        )


@transaction.atomic
def charger(mot_de_passe: str) -> dict[str, Any]:
    """Charge (ou recharge) tout le jeu identité. Rend un petit bilan."""
    perimetres = _organisation()
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
        "membres_sans_acces": len(MEMBRES_SANS_ACCES),
        "equipes": len(EQUIPES),
        "perimetres": len(perimetres),
    }
