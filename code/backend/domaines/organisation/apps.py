"""Déclaration du domaine « organisation du chantier »."""

from django.apps import AppConfig


class ConfigurationOrganisation(AppConfig):
    """MPD-2 : aucune clé étrangère sortante vers un autre domaine ; c'est la
    racine du graphe des dépendances (rapport B0 § 5.1)."""

    name = "domaines.organisation"
    label = "organisation"
    verbose_name = "Organisation du chantier"

    def ready(self) -> None:
        from domaines.organisation import demo
        from socle.demo import declarer_chargeur

        # Rang 10 : racine du graphe, chargée avant tous les autres domaines.
        declarer_chargeur(10, "organisation", demo.charger)
