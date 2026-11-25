"""Enregistrement d'un mouvement de stock (UC-1, EF-STK-01 à 03, SQ-1).

Contrôles, dans l'ordre :
  * type de mouvement ouvert à la saisie (les types employés par le serveur
    lui-même — ajustement, annulation, stock initial — ne le sont pas) ;
  * conversion de la quantité saisie vers l'unité de base (RG-S1) ;
  * motif obligatoire selon le type (RG-S3) ;
  * destination complète d'une sortie : logement du chantier du magasin,
    corps d'état, bénéficiaire (RG-S4) ;
  * saisie rétroactive au-delà de ``delai_saisie_retroactive_h`` : motif
    obligatoire (RG-S10) ; date dans le futur refusée ;
  * stock négatif autorisé et signalé, sauf paramètre contraire (RG-S7) ;
  * règle de validation déclenchée → statut A_VALIDER, le mouvement reste
    effectif (RG-S6 : « on ne bloque pas un camion devant le magasin »).

Idempotence (exigence 6.4, ET-3) : un ``uuid`` déjà reçu avec le même contenu
rend le mouvement existant sans rien écrire ; avec un autre contenu, 409.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from domaines.organisation import selecteurs as selecteurs_organisation
from domaines.organisation.models import Magasin
from domaines.referentiels import selecteurs as selecteurs_referentiels
from domaines.referentiels.models import Article, TypeMouvement
from domaines.stock.constantes import (
    CLE_DELAI_SAISIE_RETROACTIVE,
    CLE_DERIVE_HORLOGE_MAX,
    DEFAUT_DELAI_SAISIE_RETROACTIVE_H,
    DEFAUT_DERIVE_HORLOGE_MAX_MIN,
    EVENEMENT_MOUVEMENT,
    STATUT_A_VALIDER,
    STATUT_ENREGISTRE,
    TYPE_AJUSTEMENT_MOINS,
    TYPE_AJUSTEMENT_PLUS,
    TYPE_ANNULATION_MOINS,
    TYPE_ANNULATION_PLUS,
    TYPE_STOCK_INITIAL,
)
from domaines.stock.models import MouvementStock
from domaines.stock.services import parametres, projection, publications, regles
from socle.api_outils import conflit, donnee_invalide
from socle.journalisation import contexte

# Types réservés au serveur : on ne les saisit pas, on les obtient par une
# opération (inventaire, annulation, import).
TYPES_RESERVES = frozenset(
    {
        TYPE_AJUSTEMENT_PLUS,
        TYPE_AJUSTEMENT_MOINS,
        TYPE_ANNULATION_PLUS,
        TYPE_ANNULATION_MOINS,
        TYPE_STOCK_INITIAL,
    }
)


@dataclass(frozen=True)
class Saisie:
    """Ce que l'écran ou le téléphone envoie (champs du contrat simulé)."""

    magasin: Magasin
    article: Article
    type_mouvement: TypeMouvement
    quantite_saisie: Decimal
    code_unite: str | None = None
    uuid: UUID | None = None
    logement: Any = None
    corps_etat: Any = None
    beneficiaire: str | None = None
    motif: str | None = None
    reference_externe: str | None = None
    date_operation: datetime | None = None
    horodatage_appareil: datetime | None = None


def _deja_recu(saisie: Saisie, auteur: Any) -> MouvementStock | None:
    if saisie.uuid is None:
        return None
    existant = MouvementStock.objects.filter(uuid=saisie.uuid).first()
    if existant is None:
        return None
    meme = (
        existant.magasin_id == saisie.magasin.pk
        and existant.article_id == saisie.article.pk
        and existant.type_mouvement_id == saisie.type_mouvement.pk
        and existant.quantite_saisie == saisie.quantite_saisie
        and existant.utilisateur_id == auteur.pk
    )
    if not meme:
        raise conflit(
            "UUID_DEJA_UTILISE",
            "Un autre mouvement porte déjà cet identifiant. Il n'a pas été enregistré.",
        )
    return existant


def _quantite_base(saisie: Saisie) -> tuple[Decimal, str]:
    code_unite = saisie.code_unite or saisie.article.unite_mesure_id
    facteur = selecteurs_referentiels.facteur_conversion(saisie.article.pk, code_unite)
    if facteur is None:
        raise donnee_invalide("code_unite", "Cette unité ne correspond pas à cet article.")
    return (saisie.quantite_saisie * facteur).quantize(Decimal("0.001")), code_unite


def _controler_destination(saisie: Saisie) -> None:
    type_mouvement = saisie.type_mouvement
    if type_mouvement.motif_obligatoire and not saisie.motif:
        raise donnee_invalide("motif", "Indiquez le motif de ce mouvement.")
    if not type_mouvement.destination_obligatoire:
        return
    if saisie.logement is None:
        raise donnee_invalide("logement_id_logement", "Indiquez le logement de destination.")
    if saisie.corps_etat is None:
        raise donnee_invalide("corps_etat", "Indiquez le corps d'état concerné.")
    if not saisie.beneficiaire:
        raise donnee_invalide("beneficiaire", "Indiquez la personne qui reçoit le matériel.")
    du_chantier = selecteurs_organisation.logements_du_chantier(str(saisie.magasin.chantier_id))
    if not du_chantier.filter(pk=saisie.logement.pk).exists():
        raise donnee_invalide("logement_id_logement", "Ce logement n'appartient pas au chantier.")


def _controler_dates(saisie: Saisie, maintenant: datetime) -> datetime:
    date_operation = saisie.date_operation or maintenant
    id_chantier = saisie.magasin.chantier_id
    tolerance = timedelta(
        minutes=parametres.entier(
            id_chantier, CLE_DERIVE_HORLOGE_MAX, DEFAUT_DERIVE_HORLOGE_MAX_MIN
        )
    )
    if date_operation > maintenant + tolerance:
        raise donnee_invalide("date_operation", "La date du mouvement est dans le futur.")
    delai = timedelta(
        hours=parametres.entier(
            id_chantier, CLE_DELAI_SAISIE_RETROACTIVE, DEFAUT_DELAI_SAISIE_RETROACTIVE_H
        )
    )
    if maintenant - date_operation > delai and not saisie.motif:
        raise donnee_invalide(
            "motif", "Ce mouvement est ancien : justifiez la saisie tardive dans le motif."
        )
    return date_operation


def _statut_initial(type_mouvement: TypeMouvement, quantite_base: Decimal) -> str:
    """RG-S6 : seule une sortie peut être soumise à validation."""
    if type_mouvement.sens >= 0:
        return STATUT_ENREGISTRE
    declenchee = regles.regle_declenchee(EVENEMENT_MOUVEMENT, {"quantite_base": quantite_base})
    return STATUT_A_VALIDER if declenchee else STATUT_ENREGISTRE


@transaction.atomic
def enregistrer(auteur: Any, saisie: Saisie) -> tuple[MouvementStock, bool]:
    """Rend (mouvement, créé ?). ``créé`` vaut faux pour un envoi déjà reçu."""
    existant = _deja_recu(saisie, auteur)
    if existant is not None:
        return existant, False
    if saisie.type_mouvement.pk in TYPES_RESERVES:
        raise donnee_invalide(
            "type_mouvement_code_type_mouvement",
            "Ce type de mouvement est réservé aux inventaires, aux annulations et à l'import.",
        )
    if not saisie.article.actif:
        raise donnee_invalide("article_id_article", "Cet article n'est plus actif.")
    quantite_base, code_unite = _quantite_base(saisie)
    _controler_destination(saisie)
    maintenant = timezone.now()
    date_operation = _controler_dates(saisie, maintenant)
    statut = _statut_initial(saisie.type_mouvement, quantite_base)
    mouvement = inscrire(
        auteur,
        saisie.magasin,
        saisie.article,
        saisie.type_mouvement,
        quantite_base,
        quantite_saisie=saisie.quantite_saisie,
        code_unite=code_unite,
        uuid=saisie.uuid,
        statut=statut,
        logement=saisie.logement,
        corps_etat=saisie.corps_etat,
        beneficiaire=saisie.beneficiaire,
        motif=saisie.motif,
        reference_externe=saisie.reference_externe,
        date_operation=date_operation,
        horodatage_appareil=saisie.horodatage_appareil or maintenant,
    )
    if statut == STATUT_A_VALIDER:
        publications.sortie_a_valider(mouvement)
    return mouvement, True


def inscrire(
    auteur: Any,
    magasin: Magasin,
    article: Article,
    type_mouvement: TypeMouvement,
    quantite_base: Decimal,
    *,
    quantite_saisie: Decimal | None = None,
    code_unite: str | None = None,
    uuid: UUID | None = None,
    statut: str = STATUT_ENREGISTRE,
    **champs: Any,
) -> MouvementStock:
    """Écrit le mouvement au journal et recalcule la projection, dans la même
    transaction (RG-S2). Point d'écriture unique du journal : la saisie, les
    ajustements d'inventaire, les annulations et l'import y passent."""
    stock = projection.stock_courant_verrouille(magasin.pk, article.pk)
    nouvelle = stock.quantite + type_mouvement.sens * quantite_base
    if nouvelle < 0 and type_mouvement.sens < 0:
        if not parametres.stock_negatif_autorise(magasin.chantier_id):
            raise conflit(
                "STOCK_INSUFFISANT",
                f"Stock insuffisant : il reste {stock.quantite} {article.unite_mesure_id}.",
            )
    valeurs: dict[str, Any] = {
        "quantite_saisie": quantite_saisie if quantite_saisie is not None else quantite_base,
        "quantite_base": quantite_base,
        "statut_validation": statut,
        "type_mouvement": type_mouvement,
        "article": article,
        "magasin": magasin,
        "utilisateur": auteur,
        "stock_courant": stock,
        "unite_mesure_id": code_unite or article.unite_mesure_id,
        **champs,
    }
    if uuid is not None:
        valeurs["uuid"] = uuid
    mouvement = MouvementStock.objects.create(**valeurs, **contexte.champs_appareil())
    projection.recalculer(stock, nouvelle)
    return mouvement
