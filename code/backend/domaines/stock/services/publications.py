"""Événements du stock annoncés aux autres domaines (socle/evenements.py).

Le stock ne connaît pas les notifications (I-19) : il publie ce qui vient de
se passer, avec le lieu (chantier, magasin) et les champs utiles à un
message. Codes : ceux des alertes (SEUIL_MINIMAL, SEUIL_CRITIQUE,
STOCK_NEGATIF, VALIDATION_EN_RETARD), SORTIE_A_VALIDER, SORTIE_REFUSEE.
"""

from typing import Any

from domaines.stock.models import Alerte, MouvementStock, StockCourant
from socle.evenements import EvenementMetier, publier

SORTIE_A_VALIDER = "SORTIE_A_VALIDER"
SORTIE_REFUSEE = "SORTIE_REFUSEE"


def alerte_ouverte(alerte: Alerte, stock: StockCourant) -> None:
    magasin = stock.seuil_stock.magasin
    publier(
        EvenementMetier(
            code=alerte.type_alerte,
            id_objet=alerte.pk,
            id_alerte=alerte.pk,
            id_chantier=magasin.chantier_id,
            id_magasin=magasin.pk,
            contexte={"message": alerte.message},
        )
    )


def _contexte(mouvement: MouvementStock) -> dict[str, Any]:
    return {
        # Notation ordinaire sans zéros inutiles : 150, 2.5 (jamais 1.5E+2).
        "quantite": format(mouvement.quantite_saisie.normalize(), "f"),
        "unite": mouvement.unite_mesure_id,
        "article": mouvement.article.designation,
        "magasin": mouvement.magasin.nom,
        "auteur": mouvement.utilisateur.nom_complet,
        "motif": mouvement.motif or "",
    }


def sortie_a_valider(mouvement: MouvementStock) -> None:
    publier(
        EvenementMetier(
            code=SORTIE_A_VALIDER,
            id_objet=mouvement.pk,
            id_chantier=mouvement.magasin.chantier_id,
            id_magasin=mouvement.magasin_id,
            auteur=mouvement.utilisateur,
            contexte=_contexte(mouvement),
        )
    )


def sortie_refusee(mouvement: MouvementStock, valideur: Any, motif: str | None) -> None:
    publier(
        EvenementMetier(
            code=SORTIE_REFUSEE,
            id_objet=mouvement.pk,
            id_chantier=mouvement.magasin.chantier_id,
            id_magasin=mouvement.magasin_id,
            personne=mouvement.utilisateur,
            auteur=valideur,
            contexte={**_contexte(mouvement), "motif": motif or ""},
        )
    )
