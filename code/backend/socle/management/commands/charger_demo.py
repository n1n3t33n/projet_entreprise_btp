"""Commande ``charger_demo`` : jeu de démonstration de Grand-Bassam.

Appelle, dans l'ordre, le chargeur de chaque domaine inscrit dans
``socle.demo``. Le mot de passe commun des comptes de démonstration est lu
dans DEMO_MOT_DE_PASSE (fichier .env en local) : jamais écrit dans le code ni
affiché. Rejouable sans doublon. À ne lancer que sur une base de
développement ou de démonstration.
"""

from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from socle import environnement as env
from socle.demo import CHARGEURS


class Command(BaseCommand):
    help = "Charge le jeu de démonstration de Grand-Bassam, domaine par domaine (rejouable)."

    def handle(self, *args: Any, **options: Any) -> None:
        mot_de_passe = env.texte_facultatif("DEMO_MOT_DE_PASSE")
        if not mot_de_passe:
            raise CommandError("Renseignez DEMO_MOT_DE_PASSE (fichier .env) avant le chargement.")
        with transaction.atomic():
            for chargeur in CHARGEURS:
                bilan = chargeur.charger(mot_de_passe)
                detail = ", ".join(f"{nombre} {nom}" for nom, nombre in bilan.items())
                self.stdout.write(f"{chargeur.domaine} : {detail}")
