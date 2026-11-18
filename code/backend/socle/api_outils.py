"""Aides communes aux couches API des domaines, au format d'erreur unique."""

from typing import Any

from django.db import IntegrityError, transaction
from django.db.models import Model, QuerySet

from socle.erreurs import ErreurApi


def obtenir_ou_404[M: Model](objets: QuerySet[M], message: str, **filtres: Any) -> M:
    """Rend l'objet demandé ou lève une 404 au format unique, avec un message
    destiné à l'utilisateur (« Ce magasin est introuvable. »)."""
    objet = objets.filter(**filtres).first()
    if objet is None:
        raise ErreurApi(statut=404, motif="INTROUVABLE", message=message)
    return objet


def donnee_invalide(champ: str, raison: str) -> ErreurApi:
    """Erreur 400 portant sur un champ précis du corps de la requête."""
    return ErreurApi(
        statut=400,
        motif="DONNEES_INVALIDES",
        message="Certaines informations sont manquantes ou incorrectes.",
        details={champ: [raison]},
    )


def conflit(motif: str, message: str) -> ErreurApi:
    """Erreur 409 : l'opération contredit l'état actuel de l'objet."""
    return ErreurApi(statut=409, motif=motif, message=message)


def enregistrer[M: Model](objet: M, donnees: dict[str, Any]) -> M:
    """Crée ou met à jour un objet de référentiel. Un code déjà pris (les
    contraintes ``uq_*`` et les clés saisies du MPD) devient une erreur de
    saisie lisible, pas une 500.

    À la création on force l'INSERT : sans cela, pour une table dont la clé
    est un code saisi (corps d'état, type de logement…), Django mettrait à
    jour la ligne existante au lieu de refuser le doublon."""
    creation = objet._state.adding
    for champ, valeur in donnees.items():
        setattr(objet, champ, valeur)
    try:
        with transaction.atomic():
            objet.save(force_insert=creation)
    except IntegrityError as erreur:
        raise donnee_invalide("code", "Ce code est déjà utilisé.") from erreur
    return objet
