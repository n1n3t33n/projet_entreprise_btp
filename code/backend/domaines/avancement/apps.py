"""Déclaration du domaine « avancement et notifications » (vide en B1)."""

from django.apps import AppConfig


class ConfigurationAvancement(AppConfig):
    """MPD-5 : étapes de travaux, événements d'exécution, fiches de route,
    avancement agrégé, notifications métier. Arrive en B4 et B6."""

    name = "domaines.avancement"
    label = "avancement"
    verbose_name = "Avancement et notifications"
