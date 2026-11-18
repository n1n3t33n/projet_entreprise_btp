"""Déclaration de l'application technique « socle »."""

from django.apps import AppConfig


class ConfigurationSocle(AppConfig):
    """Socle de service : aucune table, des fonctions PostgreSQL partagées."""

    name = "socle"
    label = "socle"
    verbose_name = "Socle de service"
