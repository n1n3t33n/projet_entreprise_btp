"""Commande ``sauvegarder`` : sauvegarde chiffrée de la base (EF-ADM-01).

Passe par le cadre des traitements (``sauvegarder_base``) : chaque passage
est tracé dans ``execution_traitement`` et un échec déclenche une alerte
technique. À planifier sur la plateforme (au moins chaque jour ; chaque
heure si l'hébergeur n'offre pas de sauvegarde continue). Voir
``socle/sauvegarde.py`` et la procédure de restauration (README).
"""

from typing import Any

from django.core.management.base import BaseCommand, CommandError

from socle import traitements
from socle.models import STATUT_REUSSI

NOM_TRAITEMENT = "sauvegarder_base"


class Command(BaseCommand):
    help = "Crée une sauvegarde chiffrée de la base dans SAUVEGARDE_DOSSIER."

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            execution = traitements.executer(NOM_TRAITEMENT)
        except traitements.TraitementDejaEnCours as erreur:
            raise CommandError(str(erreur)) from erreur
        if execution.statut != STATUT_REUSSI:
            raise CommandError(f"Sauvegarde en échec : {execution.detail}")
        self.stdout.write(execution.detail)
