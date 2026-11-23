"""Déclaration du domaine « notifications »."""

from django.apps import AppConfig


class ConfigurationNotifications(AppConfig):
    """MPD-5, partie notifications : types, abonnements par rôle,
    notifications. Dépend des domaines identité (destinataires, rôles) et
    stock (alertes, « acheminée par ») ; aucun domaine ne dépend de lui
    (Q-AO, I-19)."""

    name = "domaines.notifications"
    label = "notifications"
    verbose_name = "Notifications"
