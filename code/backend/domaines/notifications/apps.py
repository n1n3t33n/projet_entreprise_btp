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

    def ready(self) -> None:
        from domaines.notifications import recepteurs
        from domaines.notifications.api import references
        from socle.evenements import evenement_publie
        from socle.synchronisation import declarer_reference

        # Toute publication d'un domaine peut devenir une notification (I-19).
        evenement_publie.connect(recepteurs.evenement_publie, dispatch_uid="notifications")
        # Notifications non lues transmises au mobile à chaque synchronisation (Q-AW).
        for jeu in references.JEUX:
            declarer_reference(jeu)
