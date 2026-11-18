"""Commande ``creer_partitions`` : crée d'avance les partitions mensuelles.

Rapport B0 § 4.5 : lancée à chaque déploiement (étape de publication de la
plateforme) puis chaque jour par une tâche planifiée. Idempotente : la
relancer ne crée rien de plus et ne fait que réaffirmer les droits. Elle
passe par la fonction SQL ``socle_creer_partition_mensuelle`` (SECURITY
DEFINER), donc peut tourner sous le rôle applicatif.

Elle n'a pas besoin de la table ``execution_traitement`` (arbitrage Q9) : son
résultat est entièrement vérifiable dans le catalogue PostgreSQL, et son
dernier passage est tracé dans les journaux JSON. Cette table arrivera avec le
premier traitement ordonnancé métier, en B3.
"""

import logging
from argparse import ArgumentParser
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections
from django.utils import timezone

from socle.base_de_donnees.partitions import (
    TABLES_PARTITIONNEES,
    creer_partitions,
    mois_a_couvrir,
)

journal = logging.getLogger("chantiersync.traitements")


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
        avance = options["mois_avance"]
        if avance is None:
            avance = settings.PARTITIONS_MOIS_AVANCE
        mois = mois_a_couvrir(timezone.localdate(), avance)
        noms = creer_partitions(connections[options["database"]], TABLES_PARTITIONNEES, mois)
        journal.info(
            "partitions mensuelles vérifiées",
            extra={"commande": "creer_partitions", "detail": len(noms)},
        )
        self.stdout.write(f"{len(noms)} partition(s) vérifiée(s) : {', '.join(noms)}")
