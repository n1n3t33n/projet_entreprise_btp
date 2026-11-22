"""Seuils de stock par article et par magasin (EF-STK-06, RG-S5)."""

from decimal import Decimal
from typing import Any

from django.db import transaction

from domaines.stock.models import SeuilStock
from domaines.stock.services import projection
from socle.api_outils import donnee_invalide


@transaction.atomic
def definir(id_magasin: Any, id_article: Any, minimal: Decimal, critique: Decimal) -> SeuilStock:
    """Pose les deux seuils et les active, puis reclasse le stock courant
    (une alerte s'ouvre si le stock est déjà sous un seuil)."""
    if critique > minimal:
        raise donnee_invalide(
            "seuil_critique", "Le seuil critique ne peut pas dépasser le seuil minimal."
        )
    stock = projection.stock_courant_verrouille(id_magasin, id_article)
    seuil = stock.seuil_stock
    seuil.seuil_minimal, seuil.seuil_critique, seuil.actif = minimal, critique, True
    seuil.save(update_fields=["seuil_minimal", "seuil_critique", "actif"])
    projection.recalculer(stock, stock.quantite)
    return seuil
