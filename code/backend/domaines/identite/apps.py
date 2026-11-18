"""Déclaration du domaine « identité, comptes et droits »."""

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ConfigurationIdentite(AppConfig):
    """MPD-1 (10 tables). Dépend du domaine « organisation » (``perimetre`` →
    ``chantier``, ``magasin``), jamais l'inverse (README § 9.3)."""

    name = "domaines.identite"
    label = "identite"
    verbose_name = "Identité, comptes et droits"

    def ready(self) -> None:
        # Description OpenAPI du jeton porteur (enregistrée à l'import).
        from domaines.identite import schema_openapi  # noqa: F401
        from socle.base_de_donnees.partitions import declarer_table_partitionnee

        # journal_audit est partitionnée par mois (MPD-1, MPD § 6.5) : la
        # commande creer_partitions doit la connaître.
        declarer_table_partitionnee("journal_audit")

        # Le framework de permissions de Django n'est pas utilisé (décision
        # 4.9 du rapport B0) : on ne remplit pas auth_permission, qui reste
        # vide. Les droits viennent de droit_accorde (MPD-1).
        post_migrate.disconnect(dispatch_uid="django.contrib.auth.management.create_permissions")
