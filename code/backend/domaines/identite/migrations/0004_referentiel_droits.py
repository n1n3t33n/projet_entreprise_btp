"""Identité 0004 — référentiel initial des rôles, permissions et droits.

Migration de DONNÉES, séparée des migrations de schéma (ecc:database-
migrations). Les valeurs sont recopiées ici (et non importées du code) parce
qu'une migration doit rester figée dans le temps.

Contenu :
  * les 9 rôles arbitrés (Q8), codes UPPER_SNAKE ;
  * le catalogue des permissions que le code et les fronts référencent :
      - module « api » : contrôle de chaque point d'entrée (EF-AUT-07) ;
      - module « technique » : administration Django et documentation d'API
        (exigences 6.9, 6.10, arbitrage Q5) ;
      - module « ecran » : les 11 écrans du poste de pilotage web, aux codes
        déjà utilisés par le web (« ecran.<id>.lire ») ;
      - module « mobile » : les 6 onglets de l'application mobile, pour
        remplacer la table codée en dur ``ongletsPour`` (I-06) ;
  * les droits d'AMORÇAGE seulement : l'administrateur reçoit toutes les
    permissions « api » et « technique » (sinon personne ne pourrait
    administrer une base neuve), et chaque rôle reçoit « api.session.lire »
    (consulter sa propre session). La matrice métier complète est une
    donnée de configuration : elle se règle depuis l'écran « Matrice des
    droits » (PUT /api/droits/accordes) et le jeu de démonstration la remplit.

Rôles et permissions restent des TABLES vivantes : l'administrateur peut en
ajouter sans redéploiement (MPD § 6.5).
"""

from typing import Any

from django.db import migrations

ROLES = [
    # (code, libellé, système)
    ("DIRECTION", "Direction", False),
    ("ADMINISTRATEUR", "Administrateur", True),
    ("COMMERCIAL", "Commercial", False),
    ("RESPONSABLE_TECHNIQUE", "Responsable technique", False),
    ("ACQUEREUR", "Acquéreur", False),
    ("MAGASINIER", "Magasinier", False),
    ("TECHNICIEN", "Technicien", False),
    ("CHEF_CHANTIER", "Chef de chantier", False),
    ("GESTIONNAIRE_STOCK", "Gestionnaire de stock", False),
]

# (module, ressource, action, libellé) ; code = « module.ressource.action ».
PERMISSIONS_API = [
    ("api", "session", "LIRE", "Consulter sa session et ses droits"),
    ("api", "comptes", "LIRE", "Consulter les comptes"),
    ("api", "comptes", "CREER", "Créer un compte"),
    ("api", "comptes", "MODIFIER", "Modifier ou désactiver un compte"),
    ("api", "perimetres", "LIRE", "Consulter les périmètres"),
    ("api", "droits", "LIRE", "Consulter la matrice des droits"),
    ("api", "droits", "MODIFIER", "Modifier la matrice des droits"),
    ("api", "appareils", "LIRE", "Consulter les appareils enrôlés"),
    ("api", "appareils", "MODIFIER", "Révoquer un appareil"),
    ("api", "audit", "LIRE", "Consulter le journal d'audit"),
    ("technique", "admin", "LIRE", "Ouvrir l'administration technique"),
    ("technique", "admin", "MODIFIER", "Modifier dans l'administration technique"),
    ("technique", "documentation", "LIRE", "Consulter la documentation de l'API"),
]

ECRANS_WEB = [
    ("tableau-de-bord", "Tableau de bord"),
    ("avancement", "Avancement"),
    ("journal", "Journal d'exécution"),
    ("stock", "Stock"),
    ("referentiels", "Référentiels"),
    ("gammes", "Gammes"),
    ("equipes", "Équipes"),
    ("parametrage", "Paramétrage"),
    ("administration", "Administration"),
    ("synchronisation", "Synchronisation"),
    ("espace-acquereur", "Espace acquéreur"),
]

ONGLETS_MOBILE = [
    ("stock", "Stock"),
    ("fiches", "Fiches de route"),
    ("a-valider", "À valider"),
    ("historique", "Historique"),
    ("synchro", "Synchronisation"),
    ("profil", "Profil"),
]


def _permissions() -> list[tuple[str, str, str, str]]:
    permissions = list(PERMISSIONS_API)
    permissions += [
        ("ecran", ecran, "LIRE", f"Consulter l'écran « {libelle} »")
        for ecran, libelle in ECRANS_WEB
    ]
    permissions += [
        ("mobile", onglet, "LIRE", f"Ouvrir l'onglet mobile « {libelle} »")
        for onglet, libelle in ONGLETS_MOBILE
    ]
    return permissions


def _code(module: str, ressource: str, action: str) -> str:
    return f"{module}.{ressource}.{action.lower()}"


def charger(apps: Any, schema_editor: Any) -> None:
    Role = apps.get_model("identite", "Role")
    Permission = apps.get_model("identite", "Permission")
    DroitAccorde = apps.get_model("identite", "DroitAccorde")

    for code, libelle, systeme in ROLES:
        Role.objects.update_or_create(
            code_role=code, defaults={"libelle": libelle, "systeme": systeme, "actif": True}
        )
    for module, ressource, action, libelle in _permissions():
        Permission.objects.update_or_create(
            code_permission=_code(module, ressource, action),
            defaults={
                "module": module,
                "ressource": ressource,
                "action": action,
                "libelle": libelle,
            },
        )

    # Amorçage : l'administrateur peut tout administrer…
    for module, ressource, action, _libelle in PERMISSIONS_API:
        DroitAccorde.objects.get_or_create(
            role_id="ADMINISTRATEUR",
            permission_id=_code(module, ressource, action),
            defaults={"portee": "GLOBALE"},
        )
    # … et chacun peut consulter sa propre session.
    for code, _libelle, _systeme in ROLES:
        DroitAccorde.objects.get_or_create(
            role_id=code, permission_id="api.session.lire", defaults={"portee": "GLOBALE"}
        )


def retirer(apps: Any, schema_editor: Any) -> None:
    Role = apps.get_model("identite", "Role")
    Permission = apps.get_model("identite", "Permission")
    DroitAccorde = apps.get_model("identite", "DroitAccorde")
    codes_permissions = [_code(m, r, a) for m, r, a, _l in _permissions()]
    DroitAccorde.objects.filter(permission_id__in=codes_permissions).delete()
    Permission.objects.filter(code_permission__in=codes_permissions).delete()
    Role.objects.filter(code_role__in=[code for code, _l, _s in ROLES]).delete()


class Migration(migrations.Migration):
    dependencies = [("identite", "0003_journal_audit")]

    operations = [migrations.RunPython(charger, retirer)]
