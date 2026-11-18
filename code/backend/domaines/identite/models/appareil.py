"""Appareil enrôlé (CL-1 ``Appareil``, MPD-1 table ``appareil``, ET-4).

Cycle de vie (ET-4) : non enregistré → enrôlé à la première connexion en
ligne (ACTIF) → révoqué par l'administrateur ou par la désactivation du
compte (REVOQUE, déduction I-10). Le jeton du mobile est LIÉ à un appareil :
sa révocation coupe l'accès à la requête suivante (RG-D5, SQ-5 étape 12).
"""

import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q

from domaines.identite.constantes import STATUT_APPAREIL_ACTIF, STATUTS_APPAREIL


class Appareil(models.Model):
    """Téléphone ou tablette d'un utilisateur de terrain."""

    id_appareil = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Empreinte fournie par l'application (identifiant d'installation) : sert
    # à reconnaître le même appareil à la connexion suivante.
    empreinte_materiel = models.CharField(max_length=120)
    plateforme = models.CharField(max_length=120)
    version_application = models.CharField(max_length=120)
    # Renseignée par la synchronisation (B5) ; affichée par le front (bandeau
    # « synchronisé à 06:30 », fidelite-wireframes).
    derniere_synchronisation = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=32, default=STATUT_APPAREIL_ACTIF)
    # CL-1 « Utilisateur enrôle 0..* Appareil » : multiplicité 1 côté
    # utilisateur, d'où NOT NULL.
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column="utilisateur_id_utilisateur",
        db_index=False,
        related_name="appareils",
    )

    class Meta:
        db_table = "appareil"
        verbose_name = "appareil"
        constraints = [
            models.CheckConstraint(
                condition=Q(statut__in=STATUTS_APPAREIL), name="ck_appareil_statut"
            ),
        ]
        indexes = [
            models.Index(fields=["utilisateur"], name="ix_appareil_utilisateur_id_utilisateur"),
        ]

    def __str__(self) -> str:
        return f"{self.plateforme} · {self.empreinte_materiel}"

    @property
    def est_actif(self) -> bool:
        return self.statut == STATUT_APPAREIL_ACTIF
