"""Déclaration de l'application technique « socle »."""

from django.apps import AppConfig


class ConfigurationSocle(AppConfig):
    """Socle de service : fonctions PostgreSQL partagées, table technique
    ``execution_traitement``, cadres communs (import CSV, traitements
    planifiés, métriques, alertes). Ne dépend d'aucun domaine."""

    name = "socle"
    label = "socle"
    verbose_name = "Socle de service"

    def ready(self) -> None:
        from socle.base_de_donnees.partitions import preparer_partitions
        from socle.traitements import declarer_traitement

        # Premier traitement planifié (6.5), lancé chaque jour par la plateforme.
        declarer_traitement("creer_partitions", preparer_partitions)
        # Sauvegarde chiffrée de la base (EF-ADM-01, Q-BG).
        from socle import sauvegarde

        declarer_traitement("sauvegarder_base", sauvegarde.traitement)
