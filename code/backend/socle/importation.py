"""Import CSV des référentiels (EF-ADM-02, UC-4) : lecture du fichier et
registre des cibles.

Le socle ne connaît aucune table. Chaque domaine déclare ses cibles dans son
``apps.ready()`` avec ``declarer_cible`` (organisation : chantiers et magasins ;
référentiels : articles). Une cible fournit ses colonnes, de quoi valider une
ligne et de quoi enregistrer les lignes valides.

L'import se fait en deux temps, appelés avec le même contenu :
  * ``analyser`` valide chaque ligne et rend un rapport, sans rien écrire ;
  * ``importer`` refait l'analyse côté serveur (on ne fait jamais confiance à
    un rapport renvoyé par le client), puis enregistre les lignes valides en
    une seule transaction. Les lignes en erreur sont ignorées, comme l'annonce
    l'écran (« Importer N ligne(s) »).

Le fichier : première ligne = en-tête, séparateur « ; » (tableurs
francophones) ou « , », guillemets CSV acceptés. Les colonnes sont
reconnues par leur NOM dans l'en-tête, dans n'importe quel ordre ; les
colonnes facultatives peuvent manquer. Les noms viennent du MPD (I-37).
"""

import csv
import io
from collections.abc import Callable
from dataclasses import dataclass, field

from django.db import transaction

from socle.api_outils import conflit, donnee_invalide

# Garde-fous : l'import sert aux données initiales d'un pilote, pas au
# chargement de masse. Au-delà, le fichier est refusé avant toute analyse.
TAILLE_MAXIMALE = 1_000_000  # caractères
LIGNES_MAXIMALES = 5_000

Ligne = dict[str, str]
Validateur = Callable[[Ligne], str | None]


@dataclass(frozen=True)
class Colonne:
    nom: str
    obligatoire: bool = True


@dataclass(frozen=True)
class CibleImport:
    """Une table importable.

    ``preparer`` est appelé une fois par analyse et rend le validateur d'une
    ligne : il peut charger d'avance les codes existants (unités, chantiers…)
    pour ne pas interroger la base à chaque ligne. Le validateur rend un
    message lisible, ou ``None`` si la ligne est bonne.
    ``enregistrer`` crée ou met à jour les lignes valides (par leur code) et
    rend le nombre de lignes écrites."""

    code: str
    colonnes: tuple[Colonne, ...]
    preparer: Callable[[], Validateur]
    enregistrer: Callable[[list[Ligne]], int]
    cle: str = "code"


@dataclass(frozen=True)
class LigneAnalysee:
    numero: int
    valeurs: list[str]
    erreur: str | None


@dataclass(frozen=True)
class Rapport:
    cible: str
    colonnes: list[str]
    lignes: list[LigneAnalysee] = field(default_factory=list)

    @property
    def nombre_erreurs(self) -> int:
        return sum(1 for ligne in self.lignes if ligne.erreur is not None)

    @property
    def nombre_valides(self) -> int:
        return len(self.lignes) - self.nombre_erreurs


def longueur_excessive(ligne: Ligne, limites: dict[str, int]) -> str | None:
    """Aide pour les validateurs : une valeur plus longue que sa colonne en
    base ferait échouer l'écriture ; on le dit à l'analyse."""
    for nom, limite in limites.items():
        if len(ligne.get(nom, "")) > limite:
            return f"« {nom} » dépasse {limite} caractères"
    return None


CIBLES: dict[str, CibleImport] = {}


def declarer_cible(cible: CibleImport) -> None:
    """Appelé par un domaine au démarrage. Redéclarer remplace (rechargement)."""
    CIBLES[cible.code] = cible


def cible(code: str) -> CibleImport:
    trouvee = CIBLES.get(code)
    if trouvee is None:
        raise donnee_invalide("cible", "Ce référentiel ne s'importe pas par fichier.")
    return trouvee


def _lire(contenu: str) -> list[list[str]]:
    if len(contenu) > TAILLE_MAXIMALE:
        raise donnee_invalide("contenu", "Le fichier est trop volumineux.")
    lignes = [ligne for ligne in contenu.lstrip("﻿").splitlines() if ligne.strip()]
    if not lignes:
        raise donnee_invalide("contenu", "Le fichier est vide.")
    if len(lignes) - 1 > LIGNES_MAXIMALES:
        raise donnee_invalide(
            "contenu", f"Le fichier dépasse {LIGNES_MAXIMALES} lignes : découpez-le."
        )
    separateur = ";" if ";" in lignes[0] else ","
    lecteur = csv.reader(io.StringIO("\n".join(lignes)), delimiter=separateur)
    return [[cellule.strip() for cellule in rangee] for rangee in lecteur]


def _positions(entete: list[str], attendue: CibleImport) -> dict[str, int]:
    """Position de chaque colonne attendue dans l'en-tête du fichier."""
    noms = [nom.strip().lower() for nom in entete]
    connues = [colonne.nom for colonne in attendue.colonnes]
    inconnues = [nom for nom in noms if nom not in connues]
    if inconnues:
        raise donnee_invalide(
            "contenu",
            f"Colonne(s) inconnue(s) : {', '.join(inconnues)}. "
            f"Colonnes possibles : {', '.join(connues)}.",
        )
    manquantes = [c.nom for c in attendue.colonnes if c.obligatoire and c.nom not in noms]
    if manquantes:
        raise donnee_invalide(
            "contenu", f"Colonne(s) obligatoire(s) absente(s) : {', '.join(manquantes)}."
        )
    return {nom: noms.index(nom) for nom in connues if nom in noms}


def _erreur(
    attendue: CibleImport, ligne: Ligne, cles_vues: set[str], valider: Validateur
) -> str | None:
    for colonne in attendue.colonnes:
        if colonne.obligatoire and not ligne[colonne.nom]:
            return f"« {colonne.nom} » est obligatoire"
    cle = ligne[attendue.cle].upper()
    if cle in cles_vues:
        return f"« {ligne[attendue.cle]} » apparaît deux fois dans le fichier"
    cles_vues.add(cle)
    return valider(ligne)


def _analyser(code_cible: str, contenu: str) -> tuple[Rapport, list[Ligne]]:
    attendue = cible(code_cible)
    rangees = _lire(contenu)
    entete = rangees[0]
    positions = _positions(entete, attendue)
    valider = attendue.preparer()
    colonnes = [colonne.nom for colonne in attendue.colonnes]
    lignes: list[LigneAnalysee] = []
    valides: list[Ligne] = []
    cles_vues: set[str] = set()
    for numero, rangee in enumerate(rangees[1:], start=1):
        if len(rangee) != len(entete):
            erreur = f"{len(rangee)} colonne(s) au lieu de {len(entete)} dans l'en-tête"
            lignes.append(LigneAnalysee(numero=numero, valeurs=rangee, erreur=erreur))
            continue
        ligne = {nom: rangee[positions[nom]] if nom in positions else "" for nom in colonnes}
        erreur_ligne = _erreur(attendue, ligne, cles_vues, valider)
        valeurs = [ligne[nom] for nom in colonnes]
        lignes.append(LigneAnalysee(numero=numero, valeurs=valeurs, erreur=erreur_ligne))
        if erreur_ligne is None:
            valides.append(ligne)
    return Rapport(cible=code_cible, colonnes=colonnes, lignes=lignes), valides


def analyser(code_cible: str, contenu: str) -> Rapport:
    """Premier temps : rapport ligne par ligne, aucune écriture."""
    return _analyser(code_cible, contenu)[0]


@transaction.atomic
def importer(code_cible: str, contenu: str) -> int:
    """Second temps : réanalyse puis enregistre les lignes valides, tout ou
    rien (une erreur inattendue annule l'ensemble)."""
    _rapport, valides = _analyser(code_cible, contenu)
    if not valides:
        raise conflit("RIEN_A_IMPORTER", "Aucune ligne valide à importer.")
    return cible(code_cible).enregistrer(valides)
