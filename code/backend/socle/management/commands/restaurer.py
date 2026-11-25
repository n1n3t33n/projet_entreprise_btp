"""Commande ``restaurer`` : recharge une sauvegarde chiffrée (EF-ADM-01).

Usage habituel (exercice de restauration) : créer une base VIDE, y
restaurer la dernière sauvegarde, puis comparer table par table avec la
base principale. La base principale n'est jamais écrasée sans l'option
``--ecraser-la-base-principale`` (reprise après sinistre).
"""

from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from socle import sauvegarde


class Command(BaseCommand):
    help = "Restaure une sauvegarde chiffrée dans une base, puis la compare à la base principale."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--fichier", required=True, help="Sauvegarde .dump.chiffre à charger.")
        parser.add_argument("--base", required=True, help="Base cible (vide de préférence).")
        parser.add_argument(
            "--ecraser-la-base-principale",
            action="store_true",
            help="Autorise la restauration sur la base principale (reprise après sinistre).",
        )
        parser.add_argument(
            "--sans-comparaison",
            action="store_true",
            help="Ne compare pas avec la base principale.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            sauvegarde.restaurer(
                Path(options["fichier"]), options["base"], options["ecraser_la_base_principale"]
            )
        except sauvegarde.ErreurSauvegarde as erreur:
            raise CommandError(str(erreur)) from erreur
        self.stdout.write(f"Sauvegarde restaurée dans la base « {options['base']} ».")
        if options["sans_comparaison"]:
            return
        nombre, ecarts = sauvegarde.comparer(options["base"])
        if not ecarts:
            self.stdout.write(f"Comparaison : {nombre} tables, aucun écart de nombre de lignes.")
            return
        for ecart in ecarts:
            self.stdout.write(
                f"Écart sur {ecart.table} : {ecart.source} ligne(s) dans la base principale, "
                f"{ecart.restauree} dans la base restaurée."
            )
        raise CommandError(f"Restauration incomplète : {len(ecarts)} table(s) en écart.")
