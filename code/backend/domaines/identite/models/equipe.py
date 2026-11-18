"""Équipes et appartenance (CL-1 ``Equipe``, ``MembreEquipe`` ; MPD-1).

EF-AUT-01 cite l'équipe parmi les attributs d'un compte. ``membre_equipe`` a
une clé primaire composite (utilisateur, équipe) : un utilisateur appartient
au plus une fois à une même équipe.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Equipe(models.Model):
    """Équipe de chantier (MPD-1 table ``equipe``)."""

    id_equipe = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=32)
    libelle = models.CharField(max_length=120)
    actif = models.BooleanField(default=True)

    class Meta:
        db_table = "equipe"
        verbose_name = "équipe"
        constraints = [models.UniqueConstraint(fields=["code"], name="uq_equipe_code")]

    def __str__(self) -> str:
        return self.libelle


class MembreEquipe(models.Model):
    """Appartenance d'un utilisateur à une équipe (MPD-1 ``membre_equipe``)."""

    pk = models.CompositePrimaryKey("utilisateur_id", "equipe_id")
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column="utilisateur_id_utilisateur",
        db_index=False,
        related_name="appartenances",
    )
    equipe = models.ForeignKey(
        Equipe,
        on_delete=models.PROTECT,
        db_column="equipe_id_equipe",
        db_index=False,
        related_name="membres",
    )
    est_chef_equipe = models.BooleanField(default=False)
    date_debut = models.DateField(default=timezone.localdate)
    date_fin = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "membre_equipe"
        verbose_name = "membre d'équipe"

    def __str__(self) -> str:
        return f"{self.utilisateur_id} · {self.equipe_id}"
