"""Modèles du MPD-6 côté serveur (synchronisation).

Les six autres tables du MPD-6 (file d'envoi, cache, stock et étapes locaux,
session et journal locaux) sont la base locale chiffrée du téléphone : elles
ne sont pas créées ici (arbitrage Q7-3, I-18).

Nullité tirée du MCD (règle Q-B) :
  lot_synchronisation      « émet »        appareil            (1,1) → NOT NULL
  resultat_evenement       « détaillé par » lot_synchronisation (1,1) → NOT NULL
  curseur_reference        « positionne »  appareil            (1,1), clé
  anomalie_synchronisation « signale »     appareil            (1,1) → NOT NULL
  anomalie_synchronisation « motive »      resultat_evenement  (0,1) → NULL

Aucune de ces tables n'est immuable au MPD : ce sont des traces de transport.
Les événements eux-mêmes vivent dans les journaux immuables des domaines
(mouvement_stock, evenement_validation, evenement_execution).
"""

import uuid

from django.db import models
from django.db.models import Q
from django.utils import timezone

from domaines.identite.models import Appareil
from domaines.synchronisation.constantes import (
    ANOMALIE_OUVERTE,
    STATUTS_ANOMALIE,
    STATUTS_RESULTAT,
    TYPES_ANOMALIE,
)


class LotSynchronisation(models.Model):
    """Un envoi groupé reçu d'un appareil (CL-6 ``LotSynchronisation``,
    SQ-2). ``id_lot`` est fourni par le téléphone : renvoyer le même lot rend
    les résultats déjà enregistrés (Q-AH)."""

    id_lot = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_reception = models.DateTimeField(default=timezone.now)
    nombre_evenements = models.IntegerField(default=0)
    nombre_acceptes = models.IntegerField(default=0)
    nombre_rejetes = models.IntegerField(default=0)
    duree_ms = models.IntegerField(default=0)
    appareil = models.ForeignKey(
        Appareil,
        on_delete=models.PROTECT,
        db_column="appareil_id_appareil",
        db_index=False,
        related_name="lots_synchronisation",
    )

    class Meta:
        db_table = "lot_synchronisation"
        verbose_name = "lot de synchronisation"
        indexes = [
            models.Index(fields=["appareil"], name="ix_lot_synchronisation_appareil_id_appareil"),
        ]

    def __str__(self) -> str:
        return f"lot du {self.date_reception:%Y-%m-%d %H:%M}"


class ResultatEvenement(models.Model):
    """Issue du traitement d'un événement d'un lot (CL-6
    ``ResultatEvenement``, ET-3, EF-SYN-06).

    Écarts validés (dette v0.2) :
      * index ``ix_resultat_evenement_uuid_evenement`` (Q7-5, B1) : on
        cherche si un événement a déjà été reçu, lot après lot ;
      * ``code_rejet`` : motif programmatique du rejet (``STOCK_INSUFFISANT``,
        ``SEPARATION_DES_TACHES``…), le téléphone réagit selon ce code ;
        ``motif_rejet`` garde la phrase lisible.
    """

    id_resultat = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uuid_evenement = models.UUIDField()
    statut = models.CharField(max_length=32)
    code_rejet = models.CharField(max_length=32, null=True, blank=True)  # noqa: DJ001
    motif_rejet = models.TextField(null=True, blank=True)  # noqa: DJ001
    lot_synchronisation = models.ForeignKey(
        LotSynchronisation,
        on_delete=models.PROTECT,
        db_column="lot_synchronisation_id_lot",
        db_index=False,
        related_name="resultats",
    )

    class Meta:
        db_table = "resultat_evenement"
        verbose_name = "résultat d'événement"
        constraints = [
            models.CheckConstraint(
                condition=Q(statut__in=STATUTS_RESULTAT), name="ck_resultat_evenement_statut"
            ),
        ]
        indexes = [
            models.Index(
                fields=["lot_synchronisation"],
                name="ix_resultat_evenement_lot_synchronisation_id_lot",
            ),
            models.Index(fields=["uuid_evenement"], name="ix_resultat_evenement_uuid_evenement"),
        ]

    def __str__(self) -> str:
        return f"{self.uuid_evenement} · {self.statut}"


class CurseurReference(models.Model):
    """Version d'un type de donnée de référence déjà connue d'un appareil
    (CL-6 ``CurseurReference``, EF-SYN-04). Identification relative
    (appareil, type de donnée), MLD § 6.4."""

    pk = models.CompositePrimaryKey("appareil_id", "type_donnee")
    appareil = models.ForeignKey(
        Appareil,
        on_delete=models.PROTECT,
        db_column="appareil_id_appareil",
        related_name="curseurs_reference",
    )
    type_donnee = models.CharField(max_length=32)
    version_connue = models.BigIntegerField(default=0)
    date_mise_a_jour = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "curseur_reference"
        verbose_name = "curseur de référence"

    def __str__(self) -> str:
        return f"{self.type_donnee} · {self.version_connue}"


class AnomalieSynchronisation(models.Model):
    """Anomalie détectée en synchronisation (CL-6
    ``AnomalieSynchronisation``, EF-SYN-05) : stock négatif, conflit, rejet,
    dérive d'horloge."""

    id_anomalie = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_anomalie = models.CharField(max_length=32)
    description = models.TextField()
    date_detection = models.DateTimeField(default=timezone.now)
    statut = models.CharField(max_length=32, default=ANOMALIE_OUVERTE)
    appareil = models.ForeignKey(
        Appareil,
        on_delete=models.PROTECT,
        db_column="appareil_id_appareil",
        db_index=False,
        related_name="anomalies_synchronisation",
    )
    resultat_evenement = models.ForeignKey(
        ResultatEvenement,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="resultat_evenement_id_resultat",
        db_index=False,
        related_name="anomalies",
    )

    class Meta:
        db_table = "anomalie_synchronisation"
        verbose_name = "anomalie de synchronisation"
        constraints = [
            models.CheckConstraint(
                condition=Q(type_anomalie__in=TYPES_ANOMALIE),
                name="ck_anomalie_synchronisation_type_anomalie",
            ),
            models.CheckConstraint(
                condition=Q(statut__in=STATUTS_ANOMALIE),
                name="ck_anomalie_synchronisation_statut",
            ),
        ]
        indexes = [
            models.Index(
                fields=["appareil"], name="ix_anomalie_synchronisation_appareil_id_appareil"
            ),
            models.Index(
                fields=["resultat_evenement"],
                name="ix_anomalie_synchronisation_resultat_evenement_id_resultat",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.type_anomalie} · {self.statut}"
