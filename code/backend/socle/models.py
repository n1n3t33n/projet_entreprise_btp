"""Table technique du socle : trace des traitements ordonnancés.

Écart au MPD validé (Q9 / Q-G, 2026-11-18, dette v0.2) : ``execution_
traitement`` n'appartient à aucun domaine métier. Elle répond à deux
exigences du socle de service :
  * 6.5 — un traitement ordonnancé doit pouvoir être relancé sans double effet
    et repris après une interruption : chaque passage est inscrit ici, avec son
    statut ;
  * 6.6 — la métrique « dernière exécution de chaque traitement » se lit ici.

Une ligne par passage : EN_COURS à l'ouverture, puis REUSSI ou ECHEC.
"""

import uuid

from django.db import models
from django.db.models import Q
from django.utils import timezone

STATUT_EN_COURS = "EN_COURS"
STATUT_REUSSI = "REUSSI"
STATUT_ECHEC = "ECHEC"
STATUTS_EXECUTION: tuple[str, ...] = (STATUT_EN_COURS, STATUT_REUSSI, STATUT_ECHEC)


class ExecutionTraitement(models.Model):
    """Un passage d'un traitement ordonnancé (commande de gestion lancée par
    la tâche planifiée de la plateforme, ou à la main)."""

    id_execution = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom_traitement = models.CharField(max_length=120)
    debut = models.DateTimeField(default=timezone.now)
    fin = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=32, default=STATUT_EN_COURS)
    # Bilan ou cause d'échec, en phrase lisible ; jamais de secret.
    detail = models.TextField(blank=True, default="")

    class Meta:
        db_table = "execution_traitement"
        verbose_name = "exécution de traitement"
        constraints = [
            models.CheckConstraint(
                condition=Q(statut__in=STATUTS_EXECUTION), name="ck_execution_traitement_statut"
            ),
        ]
        indexes = [
            # « Dernière exécution de chaque traitement » (métrique 6.6).
            models.Index(
                fields=["nom_traitement", "-debut"], name="ix_execution_traitement_nom_debut"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.nom_traitement} · {self.statut}"
