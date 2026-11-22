"""Lecture des comptes (EF-AUT-01, EF-AUT-02)."""

from typing import Any

from django.db.models import QuerySet

from domaines.identite.models import AffectationRole, Utilisateur
from domaines.identite.services.droits import affectations_actives


def lister() -> QuerySet[Utilisateur]:
    """Tous les comptes, par nom puis prénom (écran « Comptes » du web)."""
    return Utilisateur.objects.order_by("nom", "prenom")


def affectation_principale(utilisateur: Any) -> AffectationRole | None:
    """Affectation active la plus récente : c'est elle que décrit le contrat
    ``UtilisateurDto`` (role_code_role, perimetre_id_perimetre). Le modèle en
    permet plusieurs (EF-AUT-02) ; les autres sont servies par /auth/moi."""
    return affectations_actives(utilisateur).first()


def par_identifiant(identifiant: str) -> Utilisateur | None:
    """Un compte par son identifiant de connexion (démonstration, import)."""
    return Utilisateur.objects.filter(identifiant=identifiant).first()
