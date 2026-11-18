"""Données de démonstration du domaine « référentiels et catalogue », reprises
de la simulation du web : familles, unités et 60 articles
(``donnees-grand-bassam.ts``), corps d'état et gammes
(``gammes-grand-bassam.ts``), motifs de blocage (``avancement-grand-
bassam.ts``), règles de validation (``parametrage-grand-bassam.ts``), types de
mouvement partagés par le web et le mobile.

Différences voulues : familles plates (Q-E) ; types d'unité en majuscules ;
codes d'étape préfixés par la version de gamme (unicité du MPD, I-36). Le
type de mouvement AJU_INVENTAIRE du mobile n'est pas chargé : il n'existe pas
côté web et n'est pas arbitré (I-21).

Le type de logement est LU par le sélecteur du domaine organisation, chargé
avant celui-ci (règle de modularité).
"""

from datetime import datetime
from decimal import Decimal

from django.utils import timezone

from domaines.organisation import selecteurs as selecteurs_organisation
from domaines.referentiels.models import (
    Article,
    CategorieArticle,
    CorpsEtat,
    EtapeModele,
    Gamme,
    MotifBlocage,
    RegleValidation,
    TypeMouvement,
    UniteMesure,
)
from socle.demo import uid

CATEGORIES = [
    ("GO", "Gros œuvre"),
    ("GO-CIM", "Ciment & liants"),
    ("GO-ACI", "Aciers & treillis"),
    ("GO-AGR", "Agrégats"),
    ("SO", "Second œuvre"),
    ("SO-MAC", "Maçonnerie & cloisons"),
    ("SO-MEN", "Menuiserie"),
    ("EL", "Électricité"),
    ("PL", "Plomberie"),
    ("FIN", "Finitions"),
    ("OUT", "Outillage & EPI"),
]

UNITES = [
    ("U", "unité", "UNITE"),
    ("SAC", "sac", "MASSE"),
    ("KG", "kg", "MASSE"),
    ("T", "tonne", "MASSE"),
    ("M3", "m³", "VOLUME"),
    ("M2", "m²", "SURFACE"),
    ("ML", "ml", "LONGUEUR"),
    ("L", "litre", "VOLUME"),
    ("BTE", "boîte", "UNITE"),
    ("ROUL", "rouleau", "UNITE"),
]

# (désignation, famille, unité) — dans l'ordre du web, qui fixe les codes.
CATALOGUE = [
    ("Ciment CPJ 42.5 — sac 50 kg", "GO-CIM", "SAC"),
    ("Ciment CPA 32.5 — sac 50 kg", "GO-CIM", "SAC"),
    ("Chaux hydraulique — sac 25 kg", "GO-CIM", "SAC"),
    ("Plâtre de construction — sac 25 kg", "GO-CIM", "SAC"),
    ("Mortier colle — sac 25 kg", "GO-CIM", "SAC"),
    ("Fer à béton HA 8 mm", "GO-ACI", "ML"),
    ("Fer à béton HA 10 mm", "GO-ACI", "ML"),
    ("Fer à béton HA 12 mm", "GO-ACI", "ML"),
    ("Fer à béton HA 14 mm", "GO-ACI", "ML"),
    ("Treillis soudé ST25", "GO-ACI", "M2"),
    ("Fil d'attache recuit", "GO-ACI", "KG"),
    ("Sable de rivière lavé", "GO-AGR", "M3"),
    ("Sable de carrière", "GO-AGR", "M3"),
    ("Gravier 5/15", "GO-AGR", "M3"),
    ("Gravier 15/25", "GO-AGR", "M3"),
    ("Latérite", "GO-AGR", "M3"),
    ("Parpaing creux 15", "SO-MAC", "U"),
    ("Parpaing creux 20", "SO-MAC", "U"),
    ("Brique pleine terre cuite", "SO-MAC", "U"),
    ("Plaque de plâtre BA13", "SO-MAC", "U"),
    ("Rail métallique 48", "SO-MAC", "ML"),
    ("Montant métallique 48", "SO-MAC", "ML"),
    ("Bloc-porte intérieur 83", "SO-MEN", "U"),
    ("Bloc-porte intérieur 73", "SO-MEN", "U"),
    ("Fenêtre aluminium 120x100", "SO-MEN", "U"),
    ("Chevron sapin 63x75", "SO-MEN", "ML"),
    ("Contreplaqué 15 mm", "SO-MEN", "M2"),
    ("Câble U1000 R2V 3G2.5", "EL", "ML"),
    ("Câble U1000 R2V 3G1.5", "EL", "ML"),
    ("Gaine ICTA Ø20", "EL", "ML"),
    ("Interrupteur simple", "EL", "U"),
    ("Prise 2P+T 16 A", "EL", "U"),
    ("Disjoncteur 16 A", "EL", "U"),
    ("Disjoncteur 20 A", "EL", "U"),
    ("Tableau 2 rangées", "EL", "U"),
    ("Boîte de dérivation", "EL", "BTE"),
    ("Tube PVC évacuation Ø100", "PL", "ML"),
    ("Tube PVC évacuation Ø40", "PL", "ML"),
    ("Tube PER Ø16", "PL", "ML"),
    ("Coude PVC 100 — 87°", "PL", "U"),
    ("Siphon de sol", "PL", "U"),
    ('Robinet d’arrêt 1/2"', "PL", "U"),
    ("WC à poser complet", "PL", "U"),
    ("Lavabo céramique", "PL", "U"),
    ("Enduit de façade — sac 25 kg", "FIN", "SAC"),
    ("Peinture acrylique blanche", "FIN", "L"),
    ("Peinture glycéro", "FIN", "L"),
    ("Carrelage grès 60x60", "FIN", "M2"),
    ("Faïence murale 25x40", "FIN", "M2"),
    ("Colle à carrelage — sac 25 kg", "FIN", "SAC"),
    ("Joint de carrelage", "FIN", "KG"),
    ("Rouleau d’étanchéité", "FIN", "ROUL"),
    ("Brouette chantier 100 L", "OUT", "U"),
    ("Truelle langue de chat", "OUT", "U"),
    ("Niveau à bulle 60 cm", "OUT", "U"),
    ("Disque à tronçonner Ø230", "OUT", "U"),
    ("Casque de chantier", "OUT", "U"),
    ("Paire de gants de protection", "OUT", "U"),
    ("Gilet haute visibilité", "OUT", "U"),
    ("Chaussures de sécurité", "OUT", "U"),
]

CORPS_ETAT = [
    ("GO", "Gros œuvre", 1, "#6c8ebf"),
    ("MAC", "Maçonnerie", 2, "#b8954a"),
    ("ELEC", "Électricité", 3, "#9673a6"),
    ("PLOMB", "Plomberie", 4, "#3f8f7a"),
    ("FIN", "Finitions", 5, "#b85450"),
]

# Dix étapes types, poids total 100 (code, libellé, ordre, poids, contrôle, corps).
ETAPES = [
    ("EM-01", "Fondations", 1, 15, True, "GO"),
    ("EM-02", "Élévation des murs", 2, 15, True, "GO"),
    ("EM-03", "Cloisons", 3, 10, False, "MAC"),
    ("EM-04", "Pose des gaines", 4, 8, False, "ELEC"),
    ("EM-05", "Réseaux plomberie", 5, 8, False, "PLOMB"),
    ("EM-06", "Enduits", 6, 10, False, "MAC"),
    ("EM-07", "Appareillage électrique", 7, 8, True, "ELEC"),
    ("EM-08", "Appareils sanitaires", 8, 8, False, "PLOMB"),
    ("EM-09", "Peinture", 9, 10, False, "FIN"),
    ("EM-10", "Carrelage", 10, 8, True, "FIN"),
]

# (clé, version, libellé, statut, type de logement, préfixe des codes d'étape)
GAMMES = [
    ("G-V3-1", 1, "Villa 3 pièces — gamme standard", "ACTIVE", "VILLA3", "V3"),
    ("G-V4-1", 1, "Villa 4 pièces — gamme standard", "ACTIVE", "VILLA4", "V4"),
    ("G-DX-1", 1, "Duplex — gamme standard", "ACTIVE", "DUPLEX", "DX"),
    ("G-V3-2", 2, "Villa 3 pièces — révision isolation", "BROUILLON", "VILLA3", "V32"),
]

TYPES_MOUVEMENT = [
    ("ENT_RECEPTION", "Réception", 1, False, False),
    ("SOR_LOGEMENT", "Sortie vers un logement", -1, False, True),
    ("RET_RETOUR", "Retour au magasin", 1, True, False),
    ("SOR_PERTE", "Perte ou casse", -1, True, False),
]

MOTIFS_BLOCAGE = [
    ("MANQUE_MATERIEL", "Manque de matériel", True),
    ("ATTENTE_CLIENT", "Attente de décision client", False),
    ("INTEMPERIES", "Intempéries", False),
    ("DEFAUT_TECHNIQUE", "Défaut technique à reprendre", False),
    ("ACCES_IMPOSSIBLE", "Accès au logement impossible", False),
]

# (clé, type d'événement, champ testé, opérateur, seuil, délai en heures)
REGLES = [
    ("R-001", "VALIDATION_ETAPE", "delai_validation", "INFERIEUR_EGAL", None, 72),
    ("R-002", "ECART_INVENTAIRE", "ecart_pourcent", "SUPERIEUR_EGAL", Decimal("5.000"), None),
    ("R-003", "MOUVEMENT_STOCK", "montant", "SUPERIEUR_EGAL", Decimal("500000.000"), None),
]


def _articles() -> None:
    for rang, (designation, famille, unite) in enumerate(CATALOGUE):
        numero = f"{rang + 1:04d}"
        Article.objects.update_or_create(
            id_article=uid("article", numero),
            defaults={
                "code": f"A{numero}",
                "designation": designation,
                # Même répartition que la simulation du web.
                "origine": "PRODUCTION_INTERNE" if rang % 9 == 0 else "ACHAT",
                "code_barre": str(6_000_000_000_000 + rang * 137),
                "actif": True,
                "categorie_article_id": famille,
                "unite_mesure_id": unite,
            },
        )


def _gammes() -> int:
    nombre = 0
    for cle, version, libelle, statut, type_logement, prefixe in GAMMES:
        if selecteurs_organisation.types_logement().filter(code_type=type_logement).first() is None:
            raise LookupError("Les types de logement doivent être chargés d'abord.")
        gamme, _ = Gamme.objects.update_or_create(
            id_gamme=uid("gamme", cle),
            defaults={
                "version": version,
                "libelle": libelle,
                "statut": statut,
                "date_activation": (
                    timezone.make_aware(datetime(2026, 9, 1, 8, 0)) if statut == "ACTIVE" else None
                ),
                "type_logement_id": type_logement,
            },
        )
        for code, libelle_etape, ordre, poids, controle, corps in ETAPES:
            EtapeModele.objects.update_or_create(
                id_etape_modele=uid("etape_modele", f"{prefixe}-{code}"),
                defaults={
                    "code": f"{prefixe}-{code}",
                    "libelle": libelle_etape,
                    "ordre": ordre,
                    "poids": Decimal(poids),
                    "controle_requis": controle,
                    "gamme": gamme,
                    "corps_etat_id": corps,
                },
            )
        nombre += 1
    return nombre


def charger(mot_de_passe: str) -> dict[str, int]:
    """Crée ou met à jour les référentiels du pilote (rejouable)."""
    for code, libelle in CATEGORIES:
        CategorieArticle.objects.update_or_create(
            code_categorie=code, defaults={"libelle": libelle}
        )
    for code, libelle, type_unite in UNITES:
        UniteMesure.objects.update_or_create(
            code_unite=code, defaults={"libelle": libelle, "type_unite": type_unite}
        )
    _articles()
    for code, libelle, ordre, couleur in CORPS_ETAT:
        CorpsEtat.objects.update_or_create(
            code_corps_etat=code, defaults={"libelle": libelle, "ordre": ordre, "couleur": couleur}
        )
    gammes = _gammes()
    for code, libelle, sens, motif, destination in TYPES_MOUVEMENT:
        TypeMouvement.objects.update_or_create(
            code_type_mouvement=code,
            defaults={
                "libelle": libelle,
                "sens": sens,
                "motif_obligatoire": motif,
                "destination_obligatoire": destination,
            },
        )
    for code, libelle, requiert_article in MOTIFS_BLOCAGE:
        MotifBlocage.objects.update_or_create(
            code_motif=code,
            defaults={"libelle": libelle, "requiert_article": requiert_article, "actif": True},
        )
    for cle, type_evenement, champ, operateur, seuil, delai in REGLES:
        RegleValidation.objects.update_or_create(
            id_regle=uid("regle", cle),
            defaults={
                "type_evenement": type_evenement,
                "champ_teste": champ,
                "operateur": operateur,
                "valeur_seuil": seuil,
                "delai_heures": delai,
            },
        )
    return {
        "familles": len(CATEGORIES),
        "unités": len(UNITES),
        "articles": len(CATALOGUE),
        "corps d'état": len(CORPS_ETAT),
        "gammes": gammes,
        "types de mouvement": len(TYPES_MOUVEMENT),
        "motifs de blocage": len(MOTIFS_BLOCAGE),
        "règles": len(REGLES),
    }
