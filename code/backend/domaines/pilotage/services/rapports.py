"""Rapport hebdomadaire et indicateurs d'usage (EF-DSH-06, EF-DSH-07, I-29).

Le rapport est CALCULÉ à la demande, sans table de stockage (Q-AT) : il
assemble les rubriques que les domaines déclarent (socle/indicateurs.py),
pour une semaine ISO (lundi au dimanche). Le traitement hebdomadaire du MOT
« préparer le rapport » se réduit à prévenir la direction et le responsable
technique qu'il est disponible (notification RAPPORT_HEBDOMADAIRE, une fois
par semaine).
"""

import csv
import io
import re
import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from django.utils import timezone

from socle.api_outils import donnee_invalide
from socle.evenements import EvenementMetier, publier
from socle.indicateurs import rubriques

RAPPORT_HEBDOMADAIRE = "RAPPORT_HEBDOMADAIRE"
FORME_SEMAINE = re.compile(r"^(\d{4})-W(\d{2})$")
# Espace de nommage des identifiants de rapport : uuid5(espace, « 2026-W47 »)
# donne le même identifiant pour une même semaine (avis unique par semaine).
ESPACE_RAPPORTS = uuid.UUID("5a3f1c2e-8b7d-4e61-9a0b-2c4d6e8f1a3b")
JOURS_PAR_SEMAINE = 7


@dataclass(frozen=True)
class LigneIndicateur:
    rubrique: str
    indicateur: str
    valeur: Any


def semaine(texte: str | None) -> tuple[str, date, date]:
    """« 2026-W47 » → (code, lundi, dimanche). Sans valeur : la dernière
    semaine complète."""
    if not texte:
        aujourd_hui = timezone.localdate()
        lundi = aujourd_hui - timedelta(days=aujourd_hui.weekday() + JOURS_PAR_SEMAINE)
        annee, numero, _jour = lundi.isocalendar()
        return f"{annee}-W{numero:02d}", lundi, lundi + timedelta(days=JOURS_PAR_SEMAINE - 1)
    forme = FORME_SEMAINE.match(texte)
    if forme is None:
        raise donnee_invalide("semaine", "Indiquez la semaine sous la forme 2026-W47.")
    try:
        lundi = date.fromisocalendar(int(forme[1]), int(forme[2]), 1)
    except ValueError as erreur:
        raise donnee_invalide("semaine", "Cette semaine n'existe pas.") from erreur
    return texte, lundi, lundi + timedelta(days=JOURS_PAR_SEMAINE - 1)


def calculer(famille: str, debut: date, fin: date) -> list[LigneIndicateur]:
    return [
        LigneIndicateur(rubrique.titre, indicateur, valeur)
        for rubrique in rubriques(famille)
        for indicateur, valeur in rubrique.calculer(debut, fin)
    ]


def en_csv(lignes: list[LigneIndicateur]) -> str:
    """Point-virgule et marque d'ordre des octets : le fichier s'ouvre
    directement dans un tableur réglé en français."""
    tampon = io.StringIO()
    tampon.write("﻿")
    ecrivain = csv.writer(tampon, delimiter=";", lineterminator="\r\n")
    ecrivain.writerow(["Rubrique", "Indicateur", "Valeur"])
    for ligne in lignes:
        ecrivain.writerow([ligne.rubrique, ligne.indicateur, ligne.valeur])
    return tampon.getvalue()


def annoncer() -> str:
    """Traitement planifié ``preparer_rapport_hebdomadaire`` (le lundi) :
    annonce le rapport de la semaine écoulée, une seule fois."""
    code, _debut, _fin = semaine(None)
    publier(
        EvenementMetier(
            code=RAPPORT_HEBDOMADAIRE,
            id_objet=uuid.uuid5(ESPACE_RAPPORTS, code),
            unique=True,
            contexte={"semaine": code},
        )
    )
    return f"Rapport de la semaine {code} annoncé."
