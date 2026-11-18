"""Journal d'audit immuable et partitionné (CL-1 ``JournalAudit``, MPD-1).

RG-D9 : toute action sensible est journalisée dans un journal d'audit non
modifiable (connexions, comptes, droits, révocations…). RG-S8 : il ne se
modifie ni ne se supprime. EF-AUT-08 : il se consulte filtré par acteur, date
et action.

Mise en œuvre (rapport B0 § 4.4-4.5, arbitrage Q4), dans la migration
``0003_journal_audit`` écrite en SQL :
  * table partitionnée par mois (RANGE sur ``horodatage``) ; PostgreSQL impose
    que la clé de partition appartienne à la clé primaire, d'où la clé
    composite (id_entree, horodatage), soulignée au MPD-1 ;
  * déclencheurs qui rejettent UPDATE, DELETE et TRUNCATE ;
  * le rôle applicatif n'a que SELECT et INSERT, sur le parent et chaque
    partition, et n'est propriétaire de rien.

Conséquences assumées : aucune clé étrangère ne peut viser cette table (aucune
ne le fait au MPD, vérifié en B0), et l'admin Django ne peut pas l'afficher
(clé composite) ; elle se consulte par ``GET /api/audit``.

Écart signalé (I-27, non tranché) : le MPD n'a pas de colonne « id_objet » ;
l'objet visé par une action (quel appareil, quel compte) n'est donc pas
enregistré. Le contrat web prévoit ``id_objet`` : il est servi à ``null``.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class JournalAudit(models.Model):
    """Une entrée du journal d'audit : qui, quoi, sur quel type d'objet, quand,
    depuis quelle adresse."""

    pk = models.CompositePrimaryKey("id_entree", "horodatage")
    id_entree = models.UUIDField(default=uuid.uuid4, editable=False)
    action = models.CharField(max_length=120)
    type_objet = models.CharField(max_length=120)
    horodatage = models.DateTimeField(default=timezone.now)
    # NULL voulu (colonne nullable dans la table créée en SQL) : « adresse
    # inconnue » n'est pas une chaîne vide.
    adresse_ip = models.CharField(max_length=120, null=True, blank=True)  # noqa: DJ001
    # CL-1 « Utilisateur tracé par 0..* JournalAudit » : multiplicité 1, donc
    # NOT NULL. Une tentative de connexion avec un identifiant INCONNU n'a pas
    # d'auteur : elle ne va qu'aux journaux techniques, pas ici.
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column="utilisateur_id_utilisateur",
        db_index=False,
        related_name="entrees_audit",
    )

    class Meta:
        db_table = "journal_audit"
        verbose_name = "entrée du journal d'audit"
        indexes = [
            models.Index(
                fields=["utilisateur"], name="ix_journal_audit_utilisateur_id_utilisateur"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.horodatage:%Y-%m-%d %H:%M} · {self.action}"
