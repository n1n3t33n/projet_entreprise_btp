"""Production des notifications à partir des événements métier (EF-NOT-01).

Pour un événement publié (socle/evenements.py) dont le code est celui d'un
type de notification, chaque abonnement actif de ce type désigne ses
destinataires (Q-AQ) :
  * un rôle : les titulaires de ce rôle dont le périmètre couvre le chantier
    ou le magasin concerné, sauf l'auteur de l'action ;
  * aucun rôle : la personne concernée par l'événement.
Le message est le modèle du type, rempli avec le contexte de l'événement ;
un champ manquant reste vide plutôt que de faire échouer l'envoi.
"""

import string
from typing import Any

from domaines.identite.selecteurs.titulaires import titulaires
from domaines.notifications.models import AbonnementNotification, Notification, TypeNotification
from socle.evenements import EvenementMetier


class _Contexte(dict[str, Any]):
    def __missing__(self, cle: str) -> str:
        return ""


def rediger(modele: str, contexte: dict[str, Any]) -> str:
    """Remplit le modèle ; les accolades mal formées sont rendues telles quelles."""
    try:
        return string.Formatter().vformat(modele, (), _Contexte(contexte)).strip()
    except (ValueError, IndexError):
        return modele


def produire(evenement: EvenementMetier) -> list[Notification]:
    type_notification = TypeNotification.objects.filter(code_type=evenement.code).first()
    if type_notification is None:
        return []
    if evenement.unique and evenement.id_objet is not None:
        deja = Notification.objects.filter(
            type_notification=type_notification, id_objet=evenement.id_objet
        ).exists()
        if deja:
            return []
    abonnements = AbonnementNotification.objects.filter(
        type_notification=type_notification, actif=True
    )
    message = rediger(type_notification.modele_message, evenement.contexte)
    vus: set[Any] = set()
    notifications: list[Notification] = []
    for abonnement in abonnements:
        for destinataire in _destinataires(abonnement, evenement):
            if destinataire.pk in vus:
                continue
            vus.add(destinataire.pk)
            notifications.append(
                Notification(
                    message=message,
                    canal=abonnement.canal,
                    type_notification=type_notification,
                    utilisateur=destinataire,
                    alerte_id=evenement.id_alerte,
                    id_objet=evenement.id_objet,
                )
            )
    return Notification.objects.bulk_create(notifications)


def _destinataires(abonnement: AbonnementNotification, evenement: EvenementMetier) -> list[Any]:
    if abonnement.role_id is None:
        return [evenement.personne] if evenement.personne is not None else []
    requete = titulaires(
        abonnement.role_id, evenement.id_chantier, evenement.id_magasin, evenement.id_logement
    )
    if evenement.auteur is not None:
        requete = requete.exclude(pk=evenement.auteur.pk)
    return list(requete)
