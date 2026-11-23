"""Construction d'une saisie de mouvement à partir d'un corps validé.

Partagée par la route ``POST /mouvements`` et par la synchronisation : un
mouvement envoyé dans un lot suit exactement le même chemin (Q-AE).
"""

from typing import Any

from domaines.stock.services import acces, mouvements


def saisie_mouvement(utilisateur: Any, donnees: dict[str, Any]) -> mouvements.Saisie:
    """``donnees`` : corps validé par ``MouvementEntreeSerializer``. Le magasin
    doit être couvert par le droit de saisie (404 sinon)."""
    magasin = acces.magasin_autorise(
        utilisateur, donnees["magasin_id_magasin"], "mouvements", "CREER"
    )
    return mouvements.Saisie(
        magasin=magasin,
        article=donnees["article_id_article"],
        type_mouvement=donnees["type_mouvement_code_type_mouvement"],
        quantite_saisie=donnees["quantite_saisie"],
        code_unite=donnees.get("code_unite"),
        uuid=donnees.get("uuid"),
        logement=donnees.get("logement_id_logement"),
        corps_etat=donnees.get("corps_etat"),
        beneficiaire=donnees.get("beneficiaire") or None,
        motif=donnees.get("motif") or None,
        reference_externe=donnees.get("reference_externe") or None,
        date_operation=donnees.get("date_operation"),
        horodatage_appareil=donnees.get("horodatage_appareil"),
    )
