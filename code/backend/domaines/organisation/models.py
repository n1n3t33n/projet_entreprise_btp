"""Modèles du MPD-2 (organisation du chantier).

Noms de tables, colonnes, contraintes et index repris exactement du MPD-2.

Nullité (règle validée le 2026-11-18, I-32) : une clé étrangère est NOT NULL
quand l'entité porteuse a la cardinalité (1,1) dans le MCD-2, NULL quand elle
a (0,1). Les attributs gardent la règle de B1 : codes, libellés, statuts et
indicateurs obligatoires ; dates et valeurs naturellement facultatives
autorisées à NULL.

MCD-2 → nullité des clés étrangères :
  zone        « découpé en » chantier  (1,1) → NOT NULL
  magasin     « héberge »    chantier  (1,1) → NOT NULL
  logement    « contient »   zone      (1,1) → NOT NULL
  logement    « typé par »   type      (1,1) → NOT NULL
  parametre   « paramétré par » chantier (1,1) → NOT NULL
  acquereur   « acquis par » logement  (1,1) → NOT NULL
"""

import uuid

from django.db import models
from django.db.models import Q

from domaines.organisation.constantes import (
    STATUT_CHANTIER_ACTIF,
    STATUT_LOGEMENT_A_VENIR,
    STATUTS_CHANTIER,
    STATUTS_LOGEMENT,
    TYPES_VALEUR,
    TYPES_ZONE,
)


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


class Zone(models.Model):
    """Zone d'un chantier : bâtiment, niveau ou tranche (CL-2 ``Zone``,
    MPD-2 table ``zone``). Le code est unique sur tout le programme
    (``uq_zone_code`` du MPD)."""

    id_zone = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=32)
    nom = models.CharField(max_length=120)
    type_zone = models.CharField(max_length=32)
    chantier = models.ForeignKey(
        Chantier,
        on_delete=models.PROTECT,
        db_column="chantier_id_chantier",
        db_index=False,
        related_name="zones",
    )

    class Meta:
        db_table = "zone"
        verbose_name = "zone"
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_zone_code"),
            models.CheckConstraint(condition=Q(type_zone__in=TYPES_ZONE), name="ck_zone_type_zone"),
        ]
        indexes = [models.Index(fields=["chantier"], name="ix_zone_chantier_id_chantier")]

    def __str__(self) -> str:
        return self.nom


class TypeLogement(models.Model):
    """Type de logement (villa, duplex…), référentiel à clé varchar (CL-2
    ``TypeLogement``, MPD-2 table ``type_logement``). Chaque type porte ses
    gammes de travaux (MPD-3 ``gamme``)."""

    code_type = models.CharField(primary_key=True, max_length=32)
    libelle = models.CharField(max_length=120)
    surface_reference = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        db_table = "type_logement"
        verbose_name = "type de logement"

    def __str__(self) -> str:
        return self.libelle


class Logement(models.Model):
    """Logement d'une zone (CL-2 ``Logement``, MPD-2 table ``logement``).

    Statut = cycle de vie {A_VENIR, EN_COURS, LIVRE} (arbitrage Q-A).
    """

    id_logement = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=120)
    statut = models.CharField(max_length=32, default=STATUT_LOGEMENT_A_VENIR)
    date_livraison_prevue = models.DateField(null=True, blank=True)
    zone = models.ForeignKey(
        Zone,
        on_delete=models.PROTECT,
        db_column="zone_id_zone",
        db_index=False,
        related_name="logements",
    )
    type_logement = models.ForeignKey(
        TypeLogement,
        on_delete=models.PROTECT,
        db_column="type_logement_code_type",
        db_index=False,
        related_name="logements",
    )

    class Meta:
        db_table = "logement"
        verbose_name = "logement"
        constraints = [
            models.CheckConstraint(
                condition=Q(statut__in=STATUTS_LOGEMENT), name="ck_logement_statut"
            ),
        ]
        indexes = [
            models.Index(fields=["zone"], name="ix_logement_zone_id_zone"),
            models.Index(fields=["type_logement"], name="ix_logement_type_logement_code_type"),
        ]

    def __str__(self) -> str:
        return self.numero


class ParametreChantier(models.Model):
    """Paramètre d'un chantier, clé → valeur typée (CL-2 ``ParametreChantier``,
    MPD-2 table ``parametre_chantier`` ; EF-REF-07 « paramétrer un chantier »).

    C'est ici que vivent les seuils réglables du chantier, au lieu de
    constantes dans le code : par exemple le délai de relance des mouvements
    sans décision (``delai_relance_validation_h``, ET-2).

    Écart au MPD validé (Q-D, 2026-11-18, dette v0.2) : colonne ``libelle``,
    affichée par l'écran « Paramétrage » ; la déduire d'un catalogue écrit dans
    le code reviendrait à une valeur en dur.
    """

    id_parametre = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cle = models.CharField(max_length=32)
    valeur = models.CharField(max_length=120)
    type_valeur = models.CharField(max_length=32)
    # Écart Q-D. NULL voulu : « pas de libellé » n'est pas un libellé vide, et
    # le contrat web transporte null.
    libelle = models.CharField(max_length=120, null=True, blank=True)  # noqa: DJ001
    chantier = models.ForeignKey(
        Chantier,
        on_delete=models.PROTECT,
        db_column="chantier_id_chantier",
        db_index=False,
        related_name="parametres",
    )

    class Meta:
        db_table = "parametre_chantier"
        verbose_name = "paramètre de chantier"
        constraints = [
            models.CheckConstraint(
                condition=Q(type_valeur__in=TYPES_VALEUR),
                name="ck_parametre_chantier_type_valeur",
            ),
        ]
        indexes = [
            models.Index(fields=["chantier"], name="ix_parametre_chantier_chantier_id_chantier"),
        ]

    def __str__(self) -> str:
        return f"{self.cle} = {self.valeur}"


class Acquereur(models.Model):
    """Acquéreur d'un logement (CL-2 ``Acquereur``, MPD-2 table ``acquereur``).

    Table seule en B2 : l'espace acquéreur (UC-5, EF-ACQ-*) arrive en B7.
    Aucun lien avec un compte utilisateur au MPD (I-20).
    """

    id_acquereur = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=120)
    prenom = models.CharField(max_length=120)
    telephone = models.CharField(max_length=120, blank=True, default="")
    date_acquisition = models.DateTimeField(null=True, blank=True)
    logement = models.ForeignKey(
        Logement,
        on_delete=models.PROTECT,
        db_column="logement_id_logement",
        db_index=False,
        related_name="acquereurs",
    )

    class Meta:
        db_table = "acquereur"
        verbose_name = "acquéreur"
        indexes = [
            models.Index(fields=["logement"], name="ix_acquereur_logement_id_logement"),
        ]

    def __str__(self) -> str:
        return f"{self.prenom} {self.nom}".strip()
