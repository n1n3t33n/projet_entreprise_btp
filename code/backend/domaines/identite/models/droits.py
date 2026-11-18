"""Rôles, permissions, périmètres et leurs liaisons (CL-1, MPD-1).

Ce sont des TABLES et non des énumérations (« données en base et non du
code », MPD § 6.5) : l'administrateur fait vivre la matrice des droits sans
redéploiement (EF-AUT-02, EF-AUT-07).

Clés primaires composites (MPD-1, colonnes soulignées) : ``droit_accorde``
(permission, rôle) et ``affectation_role`` (rôle, périmètre, utilisateur).
Limites de Django 5.2 qui en découlent (rapport B0 § 4.3) : pas d'admin pour
ces modèles, aucune clé étrangère ne peut les viser (aucune ne le fait au
MPD), forme de clé figée dès cette migration.
"""

import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from domaines.identite.constantes import ACTIONS_PERMISSION, PORTEES_DROIT
from domaines.organisation.models import Chantier, Magasin


class Role(models.Model):
    """Rôle (CL-1 ``Role``, MPD-1 table ``role``) — clé primaire varchar."""

    code_role = models.CharField(primary_key=True, max_length=32)
    libelle = models.CharField(max_length=120)
    # Rôle « système » : indispensable au fonctionnement (l'administrateur).
    systeme = models.BooleanField(default=False)
    actif = models.BooleanField(default=True)

    class Meta:
        db_table = "role"
        verbose_name = "rôle"

    def __str__(self) -> str:
        return self.libelle


class Permission(models.Model):
    """Permission (CL-1 ``Permission``, MPD-1 table ``permission``).

    Une permission = un couple (module, ressource) et une action. Exemple :
    module « api », ressource « comptes », action « CREER ». Le code suit la
    forme ``module.ressource.action`` déjà utilisée par le poste web.
    """

    code_permission = models.CharField(primary_key=True, max_length=32)
    module = models.CharField(max_length=120)
    ressource = models.CharField(max_length=120)
    action = models.CharField(max_length=32)
    libelle = models.CharField(max_length=120)

    class Meta:
        db_table = "permission"
        verbose_name = "permission"
        constraints = [
            models.CheckConstraint(
                condition=Q(action__in=ACTIONS_PERMISSION), name="ck_permission_action"
            ),
        ]

    def __str__(self) -> str:
        return self.libelle


class Perimetre(models.Model):
    """Périmètre d'un rôle (CL-1 ``Perimetre``, MPD-1 table ``perimetre``).

    Délimite un chantier ou un magasin (``couvre(chantier)``,
    ``couvre(magasin)``). Sans chantier ni magasin, il couvre tout le
    programme (cas de la direction et de l'administrateur).

    I-20 : le MPD ne relie pas un périmètre à une zone ni à un logement ; la
    portée d'un droit se limite donc à {GLOBALE, PERIMETRE} (arbitrage Q8).
    """

    id_perimetre = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    libelle = models.CharField(max_length=120)
    chantier = models.ForeignKey(
        Chantier,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="chantier_id_chantier",
        db_index=False,
        related_name="perimetres",
    )
    magasin = models.ForeignKey(
        Magasin,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="magasin_id_magasin",
        db_index=False,
        related_name="perimetres",
    )

    class Meta:
        db_table = "perimetre"
        verbose_name = "périmètre"
        indexes = [
            models.Index(fields=["chantier"], name="ix_perimetre_chantier_id_chantier"),
            models.Index(fields=["magasin"], name="ix_perimetre_magasin_id_magasin"),
        ]

    def __str__(self) -> str:
        return self.libelle


class DroitAccorde(models.Model):
    """Droit accordé à un rôle (CL-1 ``DroitAccorde``, MPD-1 table
    ``droit_accorde``) : association porteuse de la portée."""

    pk = models.CompositePrimaryKey("permission_id", "role_id")
    permission = models.ForeignKey(
        Permission,
        on_delete=models.PROTECT,
        db_column="permission_code_permission",
        db_index=False,
        related_name="droits_accordes",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        db_column="role_code_role",
        db_index=False,
        related_name="droits_accordes",
    )
    portee = models.CharField(max_length=32)

    class Meta:
        db_table = "droit_accorde"
        verbose_name = "droit accordé"
        constraints = [
            models.CheckConstraint(
                condition=Q(portee__in=PORTEES_DROIT), name="ck_droit_accorde_portee"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.role_id} · {self.permission_id} ({self.portee})"


class AffectationRole(models.Model):
    """Affectation d'un rôle à un utilisateur sur un périmètre (CL-1
    ``AffectationRole``, MPD-1 table ``affectation_role``, ternaire).

    EF-AUT-02 : un utilisateur peut recevoir plusieurs rôles, chacun limité à
    un périmètre. Période d'effet DEMI-OUVERTE [date_debut, date_fin[ : une
    affectation close « le 18 » ne vaut plus le 18 (``estActive()`` de CL-1).
    """

    pk = models.CompositePrimaryKey("role_id", "perimetre_id", "utilisateur_id")
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        db_column="role_code_role",
        db_index=False,
        related_name="affectations",
    )
    perimetre = models.ForeignKey(
        Perimetre,
        on_delete=models.PROTECT,
        db_column="perimetre_id_perimetre",
        db_index=False,
        related_name="affectations",
    )
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column="utilisateur_id_utilisateur",
        db_index=False,
        related_name="affectations",
    )
    # MPD-1 : id_affectation est une colonne uuid hors clé primaire.
    id_affectation = models.UUIDField(default=uuid.uuid4, editable=False)
    date_debut = models.DateField(default=timezone.localdate)
    date_fin = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "affectation_role"
        verbose_name = "affectation de rôle"

    def __str__(self) -> str:
        return f"{self.utilisateur_id} · {self.role_id} · {self.perimetre_id}"
