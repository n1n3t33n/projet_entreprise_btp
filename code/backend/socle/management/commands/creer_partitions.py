"""Commande ``creer_partitions`` : crée d'avance les partitions mensuelles.

Rapport B0 § 4.5 : lancée à chaque déploiement (étape de publication de la
plateforme) puis chaque jour par une tâche planifiée. Idempotente : la
relancer ne crée rien de plus et ne fait que réaffirmer les droits. Elle
passe par la fonction SQL ``socle_creer_partition_mensuelle`` (SECURITY
DEFINER), donc peut tourner sous le rôle applicatif.

C'est le premier traitement du cadre ``socle/traitements.py`` (6.5) : chaque
passage est inscrit dans ``execution_traitement`` et un échec déclenche une
alerte technique. ``lancer_traitement creer_partitions`` fait la même chose
avec les réglages par défaut ; cette commande garde ses options pour les
étapes de publication déjà déclarées.
"""

from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from socle import traitements
from socle.base_de_donnees.partitions import preparer_partitions

NOM_TRAITEMENT = "creer_partitions"


class Command(BaseCommand):
    help = "Crée d'avance les partitions mensuelles des journaux immuables."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--mois-avance",
            type=int,
            default=None,
            help="Nombre de mois futurs à préparer (défaut : PARTITIONS_MOIS_AVANCE).",
        )
        parser.add_argument(
            "--database",
            default="default",
            help="Connexion à utiliser (défaut : default).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            execution = traitements.executer(
                NOM_TRAITEMENT,
                lambda: preparer_partitions(options["mois_avance"], options["database"]),
            )
        except traitements.TraitementDejaEnCours as erreur:
            raise CommandError(str(erreur)) from erreur
        self.stdout.write(execution.detail)
