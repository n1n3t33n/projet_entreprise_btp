"""Écritures du domaine « organisation du chantier » (EF-REF-01, EF-REF-02,
EF-REF-07 ; UC-3).

Les vues valident la forme des données (sérialiseurs) ; ces fonctions
appliquent les règles qui dépendent de la base : unicité des codes, une clé de
paramètre par chantier, valeur conforme à son type.
"""

from decimal import Decimal, InvalidOperation
from typing import Any

from domaines.organisation import selecteurs
from domaines.organisation.constantes import (
    TYPE_VALEUR_BOOLEEN,
    TYPE_VALEUR_DECIMAL,
    TYPE_VALEUR_ENTIER,
)
from domaines.organisation.models import Chantier, ParametreChantier
from socle.api_outils import donnee_invalide, enregistrer


def chantier_cible(id_chantier: Any) -> Chantier:
    """Chantier visé par une saisie de paramètre. L'écran « Paramétrage » du
    web ne précise pas le chantier (I-35) : on prend le chantier unique du
    pilote, sinon on demande de le préciser."""
    if id_chantier:
        chantier = selecteurs.chantiers().filter(id_chantier=id_chantier).first()
        if chantier is None:
            raise donnee_invalide("chantier_id_chantier", "Ce chantier n'existe pas.")
        return chantier
    chantier = selecteurs.chantier_unique()
    if chantier is None:
        raise donnee_invalide("chantier_id_chantier", "Précisez le chantier concerné.")
    return chantier


def _verifier_valeur(type_valeur: str, valeur: str) -> None:
    """La valeur d'un paramètre doit être lisible dans son type : un seuil en
    heures qui ne serait pas un entier casserait la relance d'ET-2."""
    try:
        if type_valeur == TYPE_VALEUR_ENTIER:
            int(valeur)
        elif type_valeur == TYPE_VALEUR_DECIMAL:
            Decimal(valeur.replace(",", "."))
        elif type_valeur == TYPE_VALEUR_BOOLEEN and valeur.lower() not in {"true", "false"}:
            raise ValueError
    except (ValueError, InvalidOperation) as erreur:
        raise donnee_invalide("valeur", "La valeur ne correspond pas au type choisi.") from erreur


def enregistrer_parametre(
    parametre: ParametreChantier, donnees: dict[str, Any], id_chantier: Any
) -> ParametreChantier:
    """Crée ou modifie un paramètre de chantier (EF-REF-07). Une clé n'existe
    qu'une fois par chantier : la règle est tenue ici, le MPD n'ayant pas de
    contrainte d'unicité sur (chantier, cle)."""
    chantier = (
        parametre.chantier
        if not parametre._state.adding and not id_chantier
        else chantier_cible(id_chantier)
    )
    _verifier_valeur(donnees["type_valeur"], donnees["valeur"])
    doublon = selecteurs.parametres(str(chantier.pk)).filter(cle=donnees["cle"])
    if not parametre._state.adding:
        doublon = doublon.exclude(pk=parametre.pk)
    if doublon.exists():
        raise donnee_invalide("cle", "Ce paramètre existe déjà pour ce chantier.")
    return enregistrer(parametre, {**donnees, "chantier": chantier})
