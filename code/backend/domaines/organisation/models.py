"""Modèles du MPD-2 nécessaires dès B1 : ``chantier`` et ``magasin``.

Noms de tables, de colonnes, de contraintes et d'index repris EXACTEMENT du
MPD-2 (``db_table`` et ``db_column`` explicites partout).

Règle de nullité (incohérence proposée I-32) : le MPD ne marque NOT NULL que
les clés primaires. On applique NOT NULL aux codes, libellés, statuts et
indicateurs, et aux clés étrangères dont la multiplicité UML vaut « 1 » ;
restent facultatifs les champs naturellement optionnels (dates de fin,
programme…). Changer une nullité ne coûte qu'une migration simple.
"""

import uuid

from django.db import models
from django.db.models import Q

from domaines.organisation.constantes import STATUT_CHANTIER_ACTIF, STATUTS_CHANTIER


class Chantier(models.Model):
    """Chantier (CL-2 ``Chantier``, MPD-2 table ``chantier``).

    Racine de l'organisation : un périmètre de droits peut couvrir un chantier
    entier (CL-1 ``Perimetre.couvre(chantier)``).
    """

    id_chantier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=32)
    nom = models.CharField(max_length=120)
    programme = models.CharField(max_length=120, blank=True, default="")
    date_debut = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=32, default=STATUT_CHANTIER_ACTIF)

    class Meta:
        db_table = "chantier"
        verbose_name = "chantier"
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_chantier_code"),
            models.CheckConstraint(
                condition=Q(statut__in=STATUTS_CHANTIER), name="ck_chantier_statut"
            ),
        ]

    def __str__(self) -> str:
        return self.nom


class Magasin(models.Model):
    """Magasin d'un chantier (CL-2 ``Magasin``, MPD-2 table ``magasin``).

    Le pilote porte sur un seul magasin (« GB-CENTRAL ») ; un périmètre de
    droits peut le viser seul (CL-1 ``Perimetre.couvre(magasin)``).
    """

    id_magasin = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=32)
    nom = models.CharField(max_length=120)
    actif = models.BooleanField(default=True)
    # MPD-2 : #chantier_id_chantier ; un magasin appartient à un chantier.
    # PROTECT : on ne supprime jamais un chantier qui porte encore un magasin.
    chantier = models.ForeignKey(
        Chantier,
        on_delete=models.PROTECT,
        db_column="chantier_id_chantier",
        db_index=False,
        related_name="magasins",
    )

    class Meta:
        db_table = "magasin"
        verbose_name = "magasin"
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_magasin_code"),
        ]
        indexes = [
            # MPD § 6.5 : toute clé étrangère hors clé primaire est indexée.
            models.Index(fields=["chantier"], name="ix_magasin_chantier_id_chantier"),
        ]

    def __str__(self) -> str:
        return self.nom
