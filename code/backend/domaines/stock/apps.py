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
        from domaines.stock import demo, importation
        from domaines.stock.api import synchronisation
        from domaines.stock.services import relance
        from socle.base_de_donnees.partitions import declarer_table_partitionnee
        from socle.demo import declarer_chargeur
        from socle.importation import declarer_cible
        from socle.synchronisation import declarer_type
        from socle.traitements import declarer_traitement

        # Partitions mensuelles préparées par le traitement creer_partitions.
        declarer_table_partitionnee("evenement_validation")
        # Rang 30 : après l'identité (auteurs des mouvements).
        declarer_chargeur(30, "stock", demo.charger)
        # Relance horaire des mouvements sans décision (ET-2), tâche planifiée
        # « lancer_traitement relancer_validations ».
        declarer_traitement("relancer_validations", relance.relancer)
        # Import CSV du stock de départ (EF-ADM-02).
        declarer_cible(importation.STOCK)
        # Mouvements et décisions saisis hors ligne, rejoués par lot (SQ-2).
        for type_evenement in synchronisation.TYPES:
            declarer_type(type_evenement)
