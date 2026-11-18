"""Déclaration du domaine « acquéreur » (phase 2, vide en B1)."""

from django.apps import AppConfig


class ConfigurationAcquereur(AppConfig):
    """Espace acquéreur en lecture seule (UC-5, EF-ACQ-*). Arrive en B7."""

    name = "domaines.acquereur"
    label = "acquereur"
    verbose_name = "Acquéreur"
