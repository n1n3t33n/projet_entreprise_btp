"""Commande ``lancer_traitement <nom>`` : point d'entrée unique de la tâche
planifiée de la plateforme (exigence 6.5).

Exemple de tâche quotidienne : ``python manage.py lancer_traitement
creer_partitions``. Sans nom, la commande liste les traitements déclarés.
Code de sortie non nul en cas d'échec ou de passage déjà en cours, pour que
la plateforme le signale.
"""

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from socle import traitements


class Command(BaseCommand):
    help = "Lance un traitement planifié et trace son passage."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("nom", nargs="?", help="Nom du traitement à lancer.")

    def handle(self, *args: Any, **options: Any) -> None:
        nom = options["nom"]
        if not nom:
            self.stdout.write(
                "Traitements déclarés : " + ", ".join(sorted(traitements.TRAITEMENTS))
            )
            return
        if nom not in traitements.TRAITEMENTS:
            raise CommandError(
                f"Traitement inconnu : « {nom} ». "
                f"Connus : {', '.join(sorted(traitements.TRAITEMENTS))}."
            )
        try:
            execution = traitements.executer(nom)
        except traitements.TraitementDejaEnCours as erreur:
            raise CommandError(str(erreur)) from erreur
        self.stdout.write(execution.detail)
