"""Déclaration du domaine « avancement et notifications »."""

from django.apps import AppConfig


class ConfigurationAvancement(AppConfig):
    """MPD-5 : étapes de travaux, événements d'exécution, fiches de route,
    avancement agrégé (B4) ; notifications métier (B6). Dépend des domaines
    organisation (logements), référentiels (gammes, motifs de blocage,
    articles) et identité (techniciens, équipes)."""

    name = "domaines.avancement"
    label = "avancement"
    verbose_name = "Avancement et notifications"

    def ready(self) -> None:
        from socle.base_de_donnees.partitions import declarer_table_partitionnee

        # Partitions mensuelles préparées par le traitement creer_partitions.
        declarer_table_partitionnee("evenement_execution")
