"""Déclaration du domaine « référentiels et catalogue » (vide en B1)."""

from django.apps import AppConfig


class ConfigurationReferentiels(AppConfig):
    """MPD-3 : catalogue d'articles, unités, gammes, types de mouvement,
    motifs de blocage, règles de validation. Arrive en B2."""

    name = "domaines.referentiels"
    label = "referentiels"
    verbose_name = "Référentiels et catalogue"
