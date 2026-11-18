"""Déclaration du domaine « organisation du chantier »."""

from django.apps import AppConfig


class ConfigurationOrganisation(AppConfig):
    """MPD-2 : aucune clé étrangère sortante vers un autre domaine ; c'est la
    racine du graphe des dépendances (rapport B0 § 5.1)."""

    name = "domaines.organisation"
    label = "organisation"
    verbose_name = "Organisation du chantier"
