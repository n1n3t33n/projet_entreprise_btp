"""Déclaration du domaine « acquéreur »."""

from django.apps import AppConfig


class ConfigurationAcquereur(AppConfig):
    """Espace acquéreur en lecture seule (UC-5, EF-ACQ-01, EF-ACQ-02, H1).
    Aucune table propre : il lit le logement de l'acquéreur rattaché au
    compte (écart Q-AY), son avancement et ses notifications. Dépend des
    domaines identité, organisation, avancement et notifications."""

    name = "domaines.acquereur"
    label = "acquereur"
    verbose_name = "Acquéreur"

    def ready(self) -> None:
        from domaines.acquereur import demo
        from socle.demo import declarer_chargeur

        # Rang 50 : après l'avancement (étapes du logement de l'acquéreur).
        declarer_chargeur(50, "acquéreur", demo.charger)
