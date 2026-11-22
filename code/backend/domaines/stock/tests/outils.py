"""Aides des tests du domaine stock : corps de requêtes et lecture du stock."""

from typing import Any

from domaines.stock.models import StockCourant


def corps_mouvement(
    donnees: dict[str, Any], type_mouvement: str, quantite: str, **champs: Any
) -> dict:
    return {
        "magasin_id_magasin": str(donnees["magasin"].pk),
        "article_id_article": str(donnees["ciment"].pk),
        "type_mouvement_code_type_mouvement": type_mouvement,
        "quantite_saisie": quantite,
        **champs,
    }


def corps_sortie(donnees: dict[str, Any], quantite: str, **champs: Any) -> dict:
    destination = {
        "logement_id_logement": str(donnees["logement"].pk),
        "corps_etat": "GO",
        "beneficiaire": "Équipe A",
    }
    return corps_mouvement(donnees, "SOR_LOGEMENT", quantite, **{**destination, **champs})


def stock_de(donnees: dict[str, Any]) -> StockCourant:
    return StockCourant.objects.get(
        seuil_stock__magasin=donnees["magasin"], seuil_stock__article=donnees["ciment"]
    )
