"""Lecture du journal d'audit (EF-AUT-08 : filtres acteur, date, action)."""

from django.db.models import QuerySet

from domaines.identite.models import JournalAudit


def lister(
    action: str | None = None, id_auteur: str | None = None, limite: int = 200
) -> QuerySet[JournalAudit]:
    """Entrées les plus récentes d'abord, filtrées par action et par auteur."""
    entrees = JournalAudit.objects.select_related("utilisateur").order_by("-horodatage")
    if action:
        entrees = entrees.filter(action=action)
    if id_auteur:
        entrees = entrees.filter(utilisateur_id=id_auteur)
    return entrees[:limite]


def dernier_auteur(action: str, id_objet: object) -> object | None:
    """Identifiant de l'auteur de la dernière entrée ``action`` visant
    ``id_objet`` (ex. qui a compté une ligne d'inventaire, RG-D11)."""
    entree = (
        JournalAudit.objects.filter(action=action, id_objet=str(id_objet))
        .order_by("-horodatage")
        .first()
    )
    return entree.utilisateur_id if entree else None
