"""Déclaration du domaine « référentiels et catalogue » (vide en B1)."""

from django.apps import AppConfig


class ConfigurationReferentiels(AppConfig):
    """MPD-3 : catalogue d'articles, unités, gammes, types de mouvement,
    motifs de blocage, règles de validation. Dépend du domaine organisation
    (une gamme vise un type de logement), jamais l'inverse."""

    name = "domaines.referentiels"
    label = "referentiels"
    verbose_name = "Référentiels et catalogue"

    def ready(self) -> None:
        from domaines.referentiels import demo
        from socle.demo import declarer_chargeur

        # Rang 15 : après l'organisation (types de logement des gammes).
        declarer_chargeur(15, "référentiels", demo.charger)
