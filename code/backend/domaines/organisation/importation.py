"""Cibles d'import CSV du domaine « organisation » (EF-ADM-02) : chantiers et
magasins. Déclarées au démarrage par ``apps.ready()`` ; le moteur commun est
dans ``socle/importation.py``.

Colonnes tirées du MPD-2, pas de la simulation du web (I-37) : le web
proposait ``libelle`` et ``ville`` pour un chantier, champs qui n'existent pas
en base. Le rapport d'analyse renvoie la liste des colonnes, l'écran s'y
adapte. Une ligne dont le code existe déjà MET À JOUR l'objet (réimporter un
fichier corrigé est sans danger).
"""

from datetime import date, datetime

from domaines.organisation import selecteurs
from domaines.organisation.constantes import STATUT_CHANTIER_ACTIF
from domaines.organisation.models import Chantier, Magasin
from socle.importation import CibleImport, Colonne, Ligne, Validateur, longueur_excessive

FORMATS_DATE = ("%Y-%m-%d", "%d/%m/%Y")


def lire_date(valeur: str) -> date | None:
    """Date au format ISO (2026-09-01) ou français (01/09/2026)."""
    for format_date in FORMATS_DATE:
        try:
            return datetime.strptime(valeur, format_date).date()
        except ValueError:
            continue
    return None


# --- Chantiers ------------------------------------------------------------------
def _preparer_chantiers() -> Validateur:
    def valider(ligne: Ligne) -> str | None:
        trop_long = longueur_excessive(ligne, {"code": 32, "nom": 120, "programme": 120})
        if trop_long:
            return trop_long
        if ligne["date_debut"] and lire_date(ligne["date_debut"]) is None:
            return "« date_debut » doit être une date (AAAA-MM-JJ ou JJ/MM/AAAA)"
        return None

    return valider


def _enregistrer_chantiers(lignes: list[Ligne]) -> int:
    for ligne in lignes:
        valeurs = {
            "nom": ligne["nom"],
            "programme": ligne["programme"],
            "date_debut": lire_date(ligne["date_debut"]) if ligne["date_debut"] else None,
        }
        # Un chantier importé naît actif ; une mise à jour ne touche pas au statut.
        Chantier.objects.update_or_create(
            code=ligne["code"],
            defaults=valeurs,
            create_defaults={**valeurs, "statut": STATUT_CHANTIER_ACTIF},
        )
    return len(lignes)


CHANTIERS = CibleImport(
    code="chantiers",
    colonnes=(
        Colonne("code"),
        Colonne("nom"),
        Colonne("programme", obligatoire=False),
        Colonne("date_debut", obligatoire=False),
    ),
    preparer=_preparer_chantiers,
    enregistrer=_enregistrer_chantiers,
)


# --- Magasins -------------------------------------------------------------------
def _preparer_magasins() -> Validateur:
    # Une seule requête pour toute l'analyse.
    chantiers = set(selecteurs.chantiers().values_list("code", flat=True))

    def valider(ligne: Ligne) -> str | None:
        trop_long = longueur_excessive(ligne, {"code": 32, "nom": 120})
        if trop_long:
            return trop_long
        if ligne["chantier"] not in chantiers:
            return f"le chantier « {ligne['chantier']} » n'existe pas"
        return None

    return valider


def _enregistrer_magasins(lignes: list[Ligne]) -> int:
    chantiers = {chantier.code: chantier for chantier in selecteurs.chantiers()}
    for ligne in lignes:
        Magasin.objects.update_or_create(
            code=ligne["code"],
            defaults={"nom": ligne["nom"], "chantier": chantiers[ligne["chantier"]]},
        )
    return len(lignes)


MAGASINS = CibleImport(
    code="magasins",
    colonnes=(Colonne("code"), Colonne("nom"), Colonne("chantier")),
    preparer=_preparer_magasins,
    enregistrer=_enregistrer_magasins,
)
