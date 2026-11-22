"""Stock de départ d'un article dans un magasin (EF-ADM-02).

RG-S2 interdit de saisir un stock : le stock de départ est donc un mouvement
d'entrée ENT_STOCK_INITIAL, inscrit au journal comme les autres. Il n'existe
qu'une fois par article et par magasin : un second import serait une double
comptabilisation, il est refusé (la correction passe par un inventaire ou un
contre-mouvement).
"""

from decimal import Decimal
from typing import Any
from uuid import UUID

from django.db import transaction

from domaines.organisation.models import Magasin
from domaines.referentiels import selecteurs as selecteurs_referentiels
from domaines.referentiels.models import Article
from domaines.stock.constantes import TYPE_STOCK_INITIAL
from domaines.stock.models import MouvementStock
from domaines.stock.services.mouvements import inscrire
from socle.api_outils import conflit

REFERENCE = "Stock de départ"


def existe(id_magasin: Any, id_article: Any) -> bool:
    return MouvementStock.objects.filter(
        magasin_id=id_magasin, article_id=id_article, type_mouvement_id=TYPE_STOCK_INITIAL
    ).exists()


@transaction.atomic
def inscrire_stock_initial(
    auteur: Any, magasin: Magasin, article: Article, quantite: Decimal, uuid: UUID | None = None
) -> MouvementStock:
    if existe(magasin.pk, article.pk):
        raise conflit(
            "STOCK_INITIAL_EXISTANT",
            "Le stock de départ de cet article est déjà enregistré dans ce magasin.",
        )
    type_mouvement = selecteurs_referentiels.type_mouvement(TYPE_STOCK_INITIAL)
    if type_mouvement is None:  # créé par la migration referentiels 0004
        raise LookupError("Type de mouvement ENT_STOCK_INITIAL absent.")
    return inscrire(
        auteur,
        magasin,
        article,
        type_mouvement,
        quantite,
        uuid=uuid,
        reference_externe=REFERENCE,
    )
