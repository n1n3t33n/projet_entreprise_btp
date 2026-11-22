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
        from django.db.models.signals import post_save

        from domaines.avancement import recepteurs
        from domaines.avancement.services import fiches
        from domaines.organisation.models import Logement
        from domaines.referentiels import signaux
        from socle.base_de_donnees.partitions import declarer_table_partitionnee
        from socle.traitements import declarer_traitement

        # Partitions mensuelles préparées par le traitement creer_partitions.
        declarer_table_partitionnee("evenement_execution")
        # Étapes créées avec le logement, ou à la publication d'une gamme (Q-AA).
        post_save.connect(
            recepteurs.logement_enregistre, sender=Logement, dispatch_uid="avancement"
        )
        signaux.gamme_publiee.connect(recepteurs.gamme_publiee, dispatch_uid="avancement")
        # Clôture quotidienne des fiches de route en fin de cycle (RG-A7).
        declarer_traitement("cycler_fiches_route", fiches.cycler)
