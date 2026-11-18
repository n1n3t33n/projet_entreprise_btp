"""Déclaration du domaine « synchronisation » (vide en B1)."""

from django.apps import AppConfig


class ConfigurationSynchronisation(AppConfig):
    """MPD-6 côté serveur : lots, résultats d'événements, curseurs,
    anomalies. Les tables locales du mobile ne sont pas créées ici
    (arbitrage Q7-3). Arrive en B5."""

    name = "domaines.synchronisation"
    label = "synchronisation"
    verbose_name = "Synchronisation"
