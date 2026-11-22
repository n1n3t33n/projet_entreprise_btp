"""Relance des mouvements restés sans décision (ET-2 « 24 h sans
décision → en alerte », MCT « relance horaire », RG-S6).

Traitement planifié ``relancer_validations`` (cadre socle/traitements.py),
lancé chaque heure par ``python manage.py lancer_traitement
relancer_validations``. Pour chaque stock courant qui a au moins un
mouvement en retard, une alerte VALIDATION_EN_RETARD est ouverte (une seule
par stock) ; elle se ferme dès qu'il n'y a plus de retard. Le passage EN_ALERTE
lui-même est un statut dérivé : il n'est écrit nulle part (Q-K).

Délai : la valeur la plus précise gagne (Q-F) — paramètre de chantier,
puis ``delai_heures`` d'une règle MOUVEMENT_STOCK, sinon pas de relance et
une alerte technique PARAMETRE_MANQUANT. La notification au valideur
relève des notifications métier (B6).

Idempotent : relancer le traitement n'ouvre pas de seconde alerte.
"""

from collections import defaultdict

from django.db import transaction

from domaines.stock import selecteurs
from domaines.stock.constantes import ALERTE_VALIDATION_EN_RETARD, STATUT_EN_ALERTE
from domaines.stock.models import Alerte, StockCourant
from domaines.stock.services import parametres, projection


def _en_retard(stock: StockCourant | None = None) -> dict[object, int]:
    """Nombre de mouvements en retard par stock courant."""
    contexte = parametres.ParametresParChantier()
    requete = selecteurs.en_attente()
    if stock is not None:
        requete = requete.filter(stock_courant=stock)
    compte: dict[object, int] = defaultdict(int)
    for mouvement in requete:
        delai = contexte.delai_relance_h(mouvement.magasin.chantier_id)
        if selecteurs.statut_derive(mouvement, delai, contexte.maintenant) == STATUT_EN_ALERTE:
            compte[mouvement.stock_courant_id] += 1
    return compte


def _message(stock: StockCourant, nombre: int) -> str:
    article, magasin = stock.seuil_stock.article, stock.seuil_stock.magasin
    return (
        f"{nombre} mouvement(s) de {article.designation} ({article.code}) au magasin "
        f"{magasin.code} attendent une décision au-delà du délai de relance."
    )


def actualiser_alerte(stock: StockCourant, nombre: int | None = None) -> None:
    """Ouvre ou ferme l'alerte de retard d'un stock selon son état actuel."""
    if nombre is None:
        nombre = _en_retard(stock).get(stock.pk, 0)
    if nombre:
        projection.ouvrir_alerte(stock, ALERTE_VALIDATION_EN_RETARD, _message(stock, nombre))
    else:
        projection.fermer_alertes(stock, [ALERTE_VALIDATION_EN_RETARD])


@transaction.atomic
def relancer() -> str:
    """Corps du traitement planifié ; rend son bilan."""
    retards = _en_retard()
    stocks = StockCourant.objects.select_related("seuil_stock__article", "seuil_stock__magasin")
    for stock in stocks.filter(pk__in=list(retards)):
        actualiser_alerte(stock, retards[stock.pk])
    ouvertes = Alerte.objects.filter(type_alerte=ALERTE_VALIDATION_EN_RETARD, statut="OUVERTE")
    for stock in stocks.filter(alertes__in=ouvertes).exclude(pk__in=list(retards)).distinct():
        actualiser_alerte(stock, 0)
    return (
        f"{sum(retards.values())} mouvement(s) en retard de décision sur "
        f"{len(retards)} article(s)."
    )
