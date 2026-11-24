"""Lectures du domaine « stock ».

Le statut d'un mouvement servi à l'écran est DÉRIVÉ (Q-K, I-13, ET-2) : la
table ne garde que le statut écrit à l'insertion, les décisions vivent dans
``evenement_validation``, l'annulation dans le contre-mouvement. Les requêtes
annotent donc chaque mouvement de sa dernière décision et de son éventuelle
annulation, en une seule requête SQL.
"""

from collections import Counter
from collections.abc import Iterable
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from django.db.models import Exists, OuterRef, QuerySet, Subquery

from domaines.stock.constantes import (
    ALERTE_OUVERTE,
    DECISION_ACCEPTE,
    DECISION_REFUSE,
    NIVEAU_CRITIQUE,
    NIVEAU_MINIMAL,
    NIVEAU_VIDE,
    STATUT_A_VALIDER,
    STATUT_ANNULE,
    STATUT_EN_ALERTE,
    STATUT_REJETE,
    STATUT_VALIDE,
)
from domaines.stock.models import (
    Alerte,
    EvenementValidation,
    Inventaire,
    MouvementStock,
    SeuilStock,
    StockCourant,
)


def lignes_stock(id_magasin: Any) -> QuerySet[SeuilStock]:
    """Articles suivis dans un magasin : un seuil existe pour chacun (créé au
    premier mouvement, Q-O), avec son stock courant."""
    return (
        SeuilStock.objects.filter(magasin_id=id_magasin)
        .select_related("article__unite_mesure", "article__categorie_article", "stock_courant")
        .order_by("article__code")
    )


def mouvements(magasins: set[UUID] | None = None) -> QuerySet[MouvementStock]:
    """Mouvements annotés pour le calcul du statut dérivé, plus récents
    d'abord. ``magasins`` : couverture de l'utilisateur (``None`` = tous)."""
    derniere_decision = (
        EvenementValidation.objects.filter(mouvement_stock=OuterRef("pk"))
        .order_by("-horodatage_serveur")
        .values("decision")[:1]
    )
    requete = MouvementStock.objects.annotate(
        derniere_decision=Subquery(derniere_decision),
        est_annule=Exists(MouvementStock.objects.filter(mouvement_annule=OuterRef("pk"))),
    ).select_related("type_mouvement", "utilisateur", "magasin")
    if magasins is not None:
        requete = requete.filter(magasin_id__in=magasins)
    return requete.order_by("-date_operation", "-horodatage_serveur")


def statut_derive(mouvement: Any, delai_relance_h: int | None, maintenant: datetime) -> str:
    """ET-2 : ANNULE si un contre-mouvement le corrige ; sinon la dernière
    décision (VALIDE, REJETE) ; sinon, s'il attend une décision, EN_ALERTE
    passé le délai de relance (Q-F), A_VALIDER avant ; sinon VALIDE (« aucune
    règle applicable »). ``mouvement`` vient de ``mouvements()``."""
    if getattr(mouvement, "est_annule", False):
        return STATUT_ANNULE
    decision = getattr(mouvement, "derniere_decision", None)
    if decision == DECISION_ACCEPTE:
        return STATUT_VALIDE
    if decision == DECISION_REFUSE:
        return STATUT_REJETE
    if mouvement.statut_validation != STATUT_A_VALIDER:
        return STATUT_VALIDE
    if delai_relance_h is not None and maintenant - mouvement.date_operation > timedelta(
        hours=delai_relance_h
    ):
        return STATUT_EN_ALERTE
    return STATUT_A_VALIDER


def en_attente(magasins: set[UUID] | None = None) -> QuerySet[MouvementStock]:
    """Mouvements soumis à validation et encore sans décision ni annulation
    (EF-STK-09), les plus anciens d'abord."""
    # Filtre sur les annotations posées par mouvements() : django-stubs ne les
    # connaît pas, d'où l'exception de typage localisée.
    sans_decision = mouvements(magasins).filter(
        statut_validation=STATUT_A_VALIDER,
        derniere_decision=None,  # type: ignore[misc]
        est_annule=False,
    )
    return sans_decision.order_by("date_operation")


def alertes_ouvertes(magasins: set[UUID] | None = None) -> QuerySet[Alerte]:
    requete = Alerte.objects.filter(statut=ALERTE_OUVERTE).select_related(
        "stock_courant__seuil_stock__article", "stock_courant__seuil_stock__magasin"
    )
    if magasins is not None:
        requete = requete.filter(stock_courant__seuil_stock__magasin_id__in=magasins)
    return requete.order_by("-date_emission")


def inventaires(magasins: set[UUID] | None = None) -> QuerySet[Inventaire]:
    requete = Inventaire.objects.select_related("magasin")
    if magasins is not None:
        requete = requete.filter(magasin_id__in=magasins)
    return requete.order_by("-date_debut")


def arborescence(magasins: Iterable[Any]) -> list[dict[str, Any]]:
    """``NoeudStock`` du web : chantier › magasin › familles (plates, Q-E),
    avec le nombre d'articles suivis par famille."""
    noeuds: dict[Any, dict[str, Any]] = {}
    for magasin in magasins:
        lignes = lignes_stock(magasin.pk)
        par_famille: Counter[tuple[str, str]] = Counter(
            (
                ligne.article.categorie_article_id or "",
                (
                    ligne.article.categorie_article.libelle
                    if ligne.article.categorie_article
                    else "Sans famille"
                ),
            )
            for ligne in lignes
        )
        chantier = noeuds.setdefault(
            magasin.chantier_id,
            {
                "id": f"ch-{magasin.chantier_id}",
                "libelle": magasin.chantier.nom,
                "type": "chantier",
                "enfants": [],
            },
        )
        chantier["enfants"].append(
            {
                "id": f"mag-{magasin.pk}",
                "libelle": magasin.nom,
                "type": "magasin",
                "nombreArticles": sum(par_famille.values()),
                "enfants": [
                    {
                        "id": f"fam-{code}",
                        "libelle": libelle,
                        "type": "famille",
                        "nombreArticles": nombre,
                        "enfants": [],
                    }
                    for (code, libelle), nombre in sorted(par_famille.items())
                ],
            }
        )
    return list(noeuds.values())


# --- Pilotage du stock (EF-DSH-04) --------------------------------------------------
def synthese(magasins: set[UUID] | None = None) -> dict[str, int]:
    """Compteurs par niveau, à la règle de l'écran (SyntheseStockDto) :
    « critique » réunit CRITIQUE et VIDE, « vigilance » est MINIMAL, « négatif »
    une quantité calculée sous zéro (MPD-4, STOCK_NEGATIF)."""
    stocks = StockCourant.objects.all()
    if magasins is not None:
        stocks = stocks.filter(seuil_stock__magasin_id__in=magasins)
    return {
        "nombre_articles": stocks.count(),
        "nombre_critique": stocks.filter(niveau_alerte__in=(NIVEAU_CRITIQUE, NIVEAU_VIDE)).count(),
        "nombre_vigilance": stocks.filter(niveau_alerte=NIVEAU_MINIMAL).count(),
        "nombre_negatif": stocks.filter(quantite__lt=0).count(),
    }


def mouvements_recents(magasins: set[UUID] | None, limite: int) -> QuerySet[MouvementStock]:
    """Derniers mouvements tous articles confondus, avec l'article et son niveau."""
    return (
        mouvements(magasins)
        .select_related("article", "stock_courant")
        .order_by("-horodatage_serveur")[:limite]
    )
