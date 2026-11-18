"""Commande ``charger_demo`` : jeu de démonstration identité de Grand-Bassam.

Le mot de passe commun des comptes de démonstration est lu dans la variable
d'environnement DEMO_MOT_DE_PASSE (fichier .env en local) : il n'est jamais
écrit dans le code ni affiché. Rejouable sans doublon.

À ne lancer que sur une base de démonstration ou de développement.
"""

from typing import Any

from django.core.management.base import BaseCommand, CommandError

from domaines.identite import demo
from socle import environnement as env


class Command(BaseCommand):
    help = "Charge le jeu de démonstration identité de Grand-Bassam (rejouable)."

    def handle(self, *args: Any, **options: Any) -> None:
        mot_de_passe = env.texte_facultatif("DEMO_MOT_DE_PASSE")
        if not mot_de_passe:
            raise CommandError("Renseignez DEMO_MOT_DE_PASSE (fichier .env) avant le chargement.")
        bilan = demo.charger(mot_de_passe)
        self.stdout.write(
            "Démonstration chargée : "
            f"{bilan['comptes']} comptes, {bilan['membres_sans_acces']} membres sans accès, "
            f"{bilan['equipes']} équipes, {bilan['perimetres']} périmètres."
        )
