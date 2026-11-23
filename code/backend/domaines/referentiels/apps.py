"""Déclaration du domaine « référentiels et catalogue »."""

from django.apps import AppConfig


class ConfigurationReferentiels(AppConfig):
    """MPD-3 : catalogue d'articles, unités, gammes, types de mouvement,
    motifs de blocage, règles de validation. Dépend du domaine organisation
    (une gamme vise un type de logement), jamais l'inverse."""

    name = "domaines.referentiels"
    label = "referentiels"
    verbose_name = "Référentiels et catalogue"

    def ready(self) -> None:
        from domaines.referentiels import demo, importation
        from domaines.referentiels.api import references
        from socle.demo import declarer_chargeur
        from socle.importation import declarer_cible
        from socle.synchronisation import declarer_reference

        # Rang 15 : après l'organisation (types de logement des gammes).
        declarer_chargeur(15, "référentiels", demo.charger)
        # Import CSV (EF-ADM-02).
        declarer_cible(importation.ARTICLES)
        # Catalogue téléchargé par le mobile hors ligne (EF-SYN-04).
        for jeu in references.JEUX:
            declarer_reference(jeu)
