"""Déclaration du domaine « synchronisation »."""

from django.apps import AppConfig


class ConfigurationSynchronisation(AppConfig):
    """MPD-6 côté serveur : lots, résultats d'événements, curseurs,
    anomalies. Les tables locales du mobile ne sont pas créées ici
    (arbitrage Q7-3)."""

    name = "domaines.synchronisation"
    label = "synchronisation"
    verbose_name = "Synchronisation"

    def ready(self) -> None:
        from domaines.synchronisation.api import evenements
        from socle.synchronisation import declarer_type

        # Résolution d'une anomalie envoyée par lot depuis le mobile (Q-AJ).
        for type_evenement in evenements.TYPES:
            declarer_type(type_evenement)
