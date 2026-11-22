"""Annulation d'un mouvement par contre-mouvement (RG-S8, EF-STK-11).

Un mouvement ne se supprime ni ne se modifie : on inscrit un mouvement de
sens opposé, de même quantité de base, justifié par un motif et relié au
mouvement corrigé (``mouvement_annule_uuid``, écart Q-L). Le statut dérivé du
mouvement d'origine devient ANNULE (ET-2). Un mouvement ne s'annule qu'une
fois (contrainte d'unicité) et un contre-mouvement ne s'annule pas : on
ressaisit alors l'opération correcte.
"""

from typing import Any

from django.db import IntegrityError, transaction

from domaines.referentiels import selecteurs as selecteurs_referentiels
from domaines.stock.constantes import TYPE_ANNULATION_MOINS, TYPE_ANNULATION_PLUS
from domaines.stock.models import MouvementStock
from domaines.stock.services import mouvements, validation
from socle.api_outils import conflit


@transaction.atomic
def annuler(auteur: Any, uuid_mouvement: Any, motif: str) -> MouvementStock:
    validation.verrouiller_mouvement(uuid_mouvement)
    origine = validation.mouvement_autorise(auteur, uuid_mouvement, "VALIDER")
    if origine.mouvement_annule_id is not None:
        raise conflit(
            "CONTRE_MOUVEMENT", "Un contre-mouvement ne s'annule pas : ressaisissez l'opération."
        )
    if getattr(origine, "est_annule", False):
        raise conflit("DEJA_ANNULE", "Ce mouvement a déjà été annulé.")
    code = TYPE_ANNULATION_PLUS if origine.type_mouvement.sens < 0 else TYPE_ANNULATION_MOINS
    type_annulation = selecteurs_referentiels.type_mouvement(code)
    if type_annulation is None:  # créé par la migration referentiels 0004
        raise LookupError(f"Type de mouvement {code} absent.")
    try:
        with transaction.atomic():
            return mouvements.inscrire(
                auteur,
                origine.magasin,
                origine.article,
                type_annulation,
                origine.quantite_base,
                motif=motif,
                mouvement_annule=origine,
            )
    except IntegrityError as erreur:  # annulation concurrente
        raise conflit("DEJA_ANNULE", "Ce mouvement a déjà été annulé.") from erreur
