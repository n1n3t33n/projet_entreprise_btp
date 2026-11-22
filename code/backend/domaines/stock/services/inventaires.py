"""Inventaire contradictoire d'un magasin (EF-STK-08, SQ-4, RG-S9).

Déroulé (SQ-4) :
  1. ouverture : une ligne par article suivi dans le magasin, quantité
     théorique figée au stock courant ; un seul inventaire ouvert par
     magasin ;
  2. comptage ligne par ligne, écart = compté − théorique ; chaque comptage
     est inscrit au journal d'audit (le MPD ne garde pas le compteur, il
     faut pouvoir contrôler RG-D11) ;
  3. soumission quand toutes les lignes sont comptées ;
  4. validation de chaque écart par un gestionnaire qui n'est PAS le
     compteur (RG-D8, RG-D11). Accepter un écart non nul inscrit un
     mouvement d'ajustement (RG-S3) ; refuser renvoie la ligne au comptage.

Double validation (RG-S9, Q-N) : si l'écart dépasse la règle de validation
ECART_INVENTAIRE (``ecart_pourcent``, 5 % dans la démonstration),
l'ajustement est inscrit « à valider » : un second gestionnaire le valide
comme une sortie (validation.py). L'auteur de l'ajustement étant le premier
valideur, RG-D8 garantit que le second est une autre personne ; le compteur
est exclu lui aussi.

L'écart est celui constaté au comptage : un mouvement survenu entre
l'ouverture et la validation n'est pas réintégré (limite assumée du pilote,
un magasin, inventaire court).
"""

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from domaines.identite.selecteurs import audit as selecteur_audit
from domaines.identite.services import audit
from domaines.referentiels import selecteurs as selecteurs_referentiels
from domaines.stock import selecteurs
from domaines.stock.constantes import (
    DECISION_REFUSE,
    EVENEMENT_ECART_INVENTAIRE,
    INVENTAIRE_A_VALIDER,
    INVENTAIRE_EN_COURS,
    INVENTAIRE_VALIDE,
    LIGNE_A_COMPTER,
    LIGNE_COMPTEE,
    LIGNE_VALIDEE,
    STATUT_A_VALIDER,
    STATUT_ENREGISTRE,
    TYPE_AJUSTEMENT_MOINS,
    TYPE_AJUSTEMENT_PLUS,
)
from domaines.stock.models import Inventaire, LigneInventaire
from domaines.stock.services import acces, regles
from domaines.stock.services.mouvements import inscrire
from socle.api_outils import conflit, donnee_invalide
from socle.erreurs import ErreurApi

AUDIT_COMPTAGE = "COMPTAGE_INVENTAIRE"
OBJET_LIGNE = "ligne_inventaire"
CENT = Decimal("100")


def inventaire_autorise(utilisateur: Any, id_inventaire: Any, action: str) -> Inventaire:
    couverts = acces.magasins_couverts(utilisateur, "inventaires", action)
    inventaire = (
        selecteurs.inventaires(couverts)
        .select_for_update(of=("self",))
        .filter(id_inventaire=id_inventaire)
        .first()
    )
    if inventaire is None:
        raise ErreurApi(statut=404, motif="INTROUVABLE", message="Cet inventaire est introuvable.")
    return inventaire


def _ligne(inventaire: Inventaire, id_ligne: Any) -> LigneInventaire:
    ligne = (
        LigneInventaire.objects.select_for_update()
        .select_related("article")
        .filter(inventaire=inventaire, id_ligne=id_ligne)
        .first()
    )
    if ligne is None:
        raise ErreurApi(statut=404, motif="INTROUVABLE", message="Cette ligne est introuvable.")
    return ligne


def _exiger(inventaire: Inventaire, statut: str, message: str) -> None:
    if inventaire.statut != statut:
        raise conflit("ETAPE_INVENTAIRE", message)


@transaction.atomic
def ouvrir(auteur: Any, id_magasin: Any) -> Inventaire:
    magasin = acces.magasin_autorise(auteur, id_magasin, "inventaires", "CREER")
    if Inventaire.objects.filter(magasin=magasin).exclude(statut=INVENTAIRE_VALIDE).exists():
        raise conflit("INVENTAIRE_EN_COURS", "Un inventaire est déjà en cours dans ce magasin.")
    inventaire = Inventaire.objects.create(magasin=magasin)
    LigneInventaire.objects.bulk_create(
        LigneInventaire(
            inventaire=inventaire,
            article_id=seuil.article_id,
            quantite_theorique=seuil.stock_courant.quantite,
        )
        for seuil in selecteurs.lignes_stock(magasin.pk)
    )
    return inventaire


@transaction.atomic
def compter(
    compteur: Any, id_inventaire: Any, id_ligne: Any, quantite: Decimal, adresse_ip: str | None
) -> LigneInventaire:
    inventaire = inventaire_autorise(compteur, id_inventaire, "MODIFIER")
    _exiger(inventaire, INVENTAIRE_EN_COURS, "Le comptage de cet inventaire est terminé.")
    ligne = _ligne(inventaire, id_ligne)
    ligne.quantite_comptee = quantite
    ligne.ecart = quantite - ligne.quantite_theorique
    ligne.statut = LIGNE_COMPTEE
    ligne.save(update_fields=["quantite_comptee", "ecart", "statut"])
    audit.consigner(compteur, AUDIT_COMPTAGE, OBJET_LIGNE, adresse_ip, ligne.pk)
    return ligne


@transaction.atomic
def soumettre(auteur: Any, id_inventaire: Any) -> Inventaire:
    inventaire = inventaire_autorise(auteur, id_inventaire, "MODIFIER")
    _exiger(inventaire, INVENTAIRE_EN_COURS, "Cet inventaire a déjà été soumis.")
    if inventaire.lignes.exclude(statut=LIGNE_COMPTEE).exists():
        raise conflit("COMPTAGE_INCOMPLET", "Toutes les lignes doivent être comptées.")
    inventaire.statut = INVENTAIRE_A_VALIDER
    inventaire.save(update_fields=["statut"])
    return inventaire


def controler_valideur(id_ligne: Any, valideur: Any) -> None:
    """RG-D8, RG-D11 : celui qui a compté une ligne ne valide ni son écart ni
    l'ajustement qui en découle."""
    if selecteur_audit.dernier_auteur(AUDIT_COMPTAGE, id_ligne) == valideur.pk:
        raise ErreurApi(
            statut=403,
            motif="SEPARATION_DES_TACHES",
            message="Vous avez compté cette ligne : une autre personne doit valider l'écart.",
        )


def ecart_pourcent(ligne: LigneInventaire) -> Decimal:
    """Écart relatif (RG-S9). Un article attendu à zéro et trouvé est un écart
    total (100 %)."""
    if ligne.quantite_theorique == 0:
        return CENT if ligne.ecart else Decimal("0")
    return abs(ligne.ecart or 0) / abs(ligne.quantite_theorique) * CENT


def _ajuster(
    valideur: Any, inventaire: Inventaire, ligne: LigneInventaire, motif: str | None
) -> None:
    ecart = ligne.ecart or Decimal("0")
    if ecart == 0:
        return
    code = TYPE_AJUSTEMENT_PLUS if ecart > 0 else TYPE_AJUSTEMENT_MOINS
    type_ajustement = selecteurs_referentiels.type_mouvement(code)
    if type_ajustement is None:  # créé par la migration referentiels 0004
        raise LookupError(f"Type de mouvement {code} absent.")
    double = regles.regle_declenchee(
        EVENEMENT_ECART_INVENTAIRE, {"ecart_pourcent": ecart_pourcent(ligne)}
    )
    inscrire(
        valideur,
        inventaire.magasin,
        ligne.article,
        type_ajustement,
        abs(ecart),
        statut=STATUT_A_VALIDER if double else STATUT_ENREGISTRE,
        ligne_inventaire=ligne,
        motif=motif or f"Ajustement de l'inventaire du {inventaire.date_debut:%d/%m/%Y}",
    )


@transaction.atomic
def valider_ligne(
    valideur: Any, id_inventaire: Any, id_ligne: Any, decision: str, motif: str | None
) -> Inventaire:
    inventaire = inventaire_autorise(valideur, id_inventaire, "VALIDER")
    _exiger(inventaire, INVENTAIRE_A_VALIDER, "Cet inventaire n'attend pas de validation.")
    ligne = _ligne(inventaire, id_ligne)
    if ligne.statut != LIGNE_COMPTEE:
        raise conflit("LIGNE_DEJA_TRAITEE", "Cette ligne a déjà été validée.")
    controler_valideur(ligne.pk, valideur)
    if decision == DECISION_REFUSE:
        if not motif:
            raise donnee_invalide("motif", "Indiquez pourquoi la ligne doit être recomptée.")
        ligne.quantite_comptee, ligne.ecart, ligne.statut = None, None, LIGNE_A_COMPTER
        ligne.save(update_fields=["quantite_comptee", "ecart", "statut"])
        inventaire.statut = INVENTAIRE_EN_COURS
        inventaire.save(update_fields=["statut"])
        return inventaire
    _ajuster(valideur, inventaire, ligne, motif)
    ligne.statut = LIGNE_VALIDEE
    ligne.save(update_fields=["statut"])
    if not inventaire.lignes.exclude(statut=LIGNE_VALIDEE).exists():
        inventaire.statut, inventaire.date_fin = INVENTAIRE_VALIDE, timezone.localdate()
        inventaire.save(update_fields=["statut", "date_fin"])
    return inventaire
