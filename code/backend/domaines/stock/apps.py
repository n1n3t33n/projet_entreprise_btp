"""Déclaration du domaine « stock et journal immuable » (vide en B1)."""

from django.apps import AppConfig


class ConfigurationStock(AppConfig):
    """MPD-4 : mouvements immuables, seuils, stock courant, alertes,
    inventaires. Arrive en B3."""

    name = "domaines.stock"
    label = "stock"
    verbose_name = "Stock et journal immuable"
