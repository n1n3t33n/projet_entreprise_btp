"""Modèles du MPD-5, partie notifications (CL-5, EF-NOT-01).

Les tables appartiennent au MPD-5 « avancement et notifications » ; leur code
vit dans un domaine à part (Q-AO) pour que ni le stock ni l'avancement ne
dépendent des notifications : ce domaine s'abonne aux événements publiés
(socle/evenements.py, I-19).

Nullité tirée du MCD (règle Q-B) :
  notification            « qualifie »       type_notification (1,1) → NOT NULL
  notification            « destinataire de » utilisateur      (1,1) → NOT NULL
  notification            « acheminée par »  alerte            (1,1) → NULL (écart Q-AN)
  abonnement_notification « abonné par »     type_notification (1,1) → NOT NULL
  abonnement_notification « abonne »         role              (0,1) → NULL
"""

import uuid

from django.db import models
from django.db.models import Q
from django.utils import timezone

from domaines.identite.models import Role, Utilisateur
from domaines.notifications.constantes import APPLICATION, CANAUX
from domaines.stock.models import Alerte


class TypeNotification(models.Model):
    """Type de notification (CL-5 ``TypeNotification``) : libellé et modèle
    du message, canal par défaut."""

    code_type = models.CharField(primary_key=True, max_length=32)
    libelle = models.CharField(max_length=120)
    modele_message = models.TextField()
    canal_defaut = models.CharField(max_length=32, default=APPLICATION)

    class Meta:
        db_table = "type_notification"
        verbose_name = "type de notification"
        constraints = [
            models.CheckConstraint(
                condition=Q(canal_defaut__in=CANAUX), name="ck_type_notification_canal_defaut"
            ),
        ]

    def __str__(self) -> str:
        return self.libelle


class AbonnementNotification(models.Model):
    """Rôle abonné à un type de notification (CL-5
    ``AbonnementNotification``). Sans rôle : la personne concernée par
    l'événement est seule destinataire (Q-AQ)."""

    id_abonnement = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    canal = models.CharField(max_length=32, default=APPLICATION)
    actif = models.BooleanField(default=True)
    type_notification = models.ForeignKey(
        TypeNotification,
        on_delete=models.PROTECT,
        db_column="type_notification_code_type",
        db_index=False,
        related_name="abonnements",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="role_code_role",
        db_index=False,
        related_name="abonnements_notification",
    )

    class Meta:
        db_table = "abonnement_notification"
        verbose_name = "abonnement à une notification"
        constraints = [
            models.CheckConstraint(
                condition=Q(canal__in=CANAUX), name="ck_abonnement_notification_canal"
            ),
        ]
        indexes = [
            models.Index(
                fields=["type_notification"],
                name="ix_abonnement_notification_type_notification_code_type",
            ),
            models.Index(fields=["role"], name="ix_abonnement_notification_role_code_role"),
        ]

    def __str__(self) -> str:
        return f"{self.type_notification_id} → {self.role_id or 'personne concernée'}"


class Notification(models.Model):
    """Notification adressée à un utilisateur (CL-5 ``Notification``).

    Écarts validés (dette v0.2, Q-AN) :
      * ``alerte`` facultative : le MCD impose qu'une notification soit
        « acheminée par » une alerte de stock, ce qui interdirait de notifier
        une étape rejetée ou une sortie à valider (EF-NOT-01, I-48) ;
      * ``id_objet`` : identifiant de l'objet en cause (mouvement, étape,
        anomalie…) pour que l'écran l'ouvre directement, comme
        ``journal_audit.id_objet`` (Q-C).
    """

    id_notification = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.TextField()
    canal = models.CharField(max_length=32, default=APPLICATION)
    date_creation = models.DateTimeField(default=timezone.now)
    date_lecture = models.DateTimeField(null=True, blank=True)
    id_objet = models.UUIDField(null=True, blank=True)
    type_notification = models.ForeignKey(
        TypeNotification,
        on_delete=models.PROTECT,
        db_column="type_notification_code_type",
        db_index=False,
        related_name="notifications",
    )
    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.PROTECT,
        db_column="utilisateur_id_utilisateur",
        db_index=False,
        related_name="notifications",
    )
    alerte = models.ForeignKey(
        Alerte,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="alerte_id_alerte",
        db_index=False,
        related_name="notifications",
    )

    class Meta:
        db_table = "notification"
        verbose_name = "notification"
        constraints = [
            models.CheckConstraint(condition=Q(canal__in=CANAUX), name="ck_notification_canal"),
        ]
        indexes = [
            models.Index(
                fields=["type_notification"], name="ix_notification_type_notification_code_type"
            ),
            models.Index(fields=["utilisateur"], name="ix_notification_utilisateur_id_utilisateur"),
            models.Index(fields=["alerte"], name="ix_notification_alerte_id_alerte"),
            models.Index(
                fields=["utilisateur", "-date_creation"], name="ix_notification_destinataire"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.type_notification_id} · {self.utilisateur_id}"
