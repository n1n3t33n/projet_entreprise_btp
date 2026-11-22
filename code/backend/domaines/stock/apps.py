"""Déclaration du domaine « stock et journal immuable »."""

from django.apps import AppConfig


class ConfigurationStock(AppConfig):
    """MPD-4 : mouvements immuables, validations, seuils, stock courant,
    alertes de stock, inventaires. Dépend des domaines organisation
    (magasins, logements), référentiels (articles, types de mouvement,
    règles) et identité (auteurs, valideurs)."""

    name = "domaines.stock"
    label = "stock"
    verbose_name = "Stock et journal immuable"

    def ready(self) -> None:
        from socle.base_de_donnees.partitions import declarer_table_partitionnee

        # Partitions mensuelles préparées par le traitement creer_partitions.
        declarer_table_partitionnee("evenement_validation")
