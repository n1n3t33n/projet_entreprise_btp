"""Modèles du MPD-4 (stock et journal immuable).

Noms repris exactement du MPD-4. Nullité des clés étrangères tirée du MCD
(règle Q-B : (1,1) → NOT NULL, (0,1) → NULL) :
  mouvement_stock       « qualifie »        type_mouvement   (1,1) → NOT NULL
  mouvement_stock       « mouvementé par »  article          (1,1) → NOT NULL
  mouvement_stock       « lieu de »         magasin          (1,1) → NOT NULL
  mouvement_stock       « saisi par »       utilisateur      (1,1) → NOT NULL
  mouvement_stock       « alimente »        stock_courant    (1,1) → NOT NULL
  mouvement_stock       « ajustée par »     ligne_inventaire (0,1) → NULL
  mouvement_stock       « destination de »  logement         (1,1) au MCD, mais
      NULL ici : seule une sortie a une destination (RG-S4,
      type_mouvement.destination_obligatoire). Incohérence du MCD, I-38.
  evenement_validation  « statué par »      mouvement_stock  (1,1) → NOT NULL
  evenement_validation  « déclenche »       regle_validation (0,1) → NULL
  evenement_validation  « décidé par »      utilisateur      (1,1) → NOT NULL
  seuil_stock           « défini pour »     magasin          (1,1) → NOT NULL
  seuil_stock           « seuillé par »     article          (1,1) → NOT NULL
  stock_courant         « compare à »       seuil_stock      (1,1), clé primaire
  alerte                « déclenche »       stock_courant    (1,1) → NOT NULL
  inventaire            « inventorié par »  magasin          (1,1) → NOT NULL
  ligne_inventaire      « composé de »      inventaire       (1,1) → NOT NULL
  ligne_inventaire      « compté dans »     article          (1,1) → NOT NULL

Deux tables sont immuables (RG-S8) : ``mouvement_stock`` et
``evenement_validation``. Déclencheurs et droits sont posés par la migration
``stock 0002`` ; ``evenement_validation`` y est créée en SQL, partitionnée par
mois. ``mouvement_stock`` ne l'est pas : partitionnement « différé » au MPD,
parce qu'``evenement_validation`` la référence (README de modélisation § 6.5).

Les quantités sont en numeric(14,3), jamais en flottant (MPD § 6.5).
"""

import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from domaines.organisation.models import Logement, Magasin
from domaines.referentiels.models import (
    Article,
    CorpsEtat,
    RegleValidation,
    TypeMouvement,
    UniteMesure,
)
from domaines.stock.constantes import (
    DECISIONS,
    INVENTAIRE_EN_COURS,
    LIGNE_A_COMPTER,
    NIVEAU_NORMAL,
    NIVEAUX,
    STATUT_A_VALIDER,
    STATUT_ENREGISTRE,
    STATUTS_ALERTE,
    STATUTS_INVENTAIRE,
    STATUTS_LIGNE,
    STATUTS_VALIDATION,
    TYPES_ALERTE,
)


def _quantite(**options: object) -> models.DecimalField:  # type: ignore[type-arg]
    return models.DecimalField(max_digits=14, decimal_places=3, **options)  # type: ignore[arg-type]


class SeuilStock(models.Model):
    """Seuils minimal et critique d'un article dans un magasin (CL-4
    ``SeuilStock``, RG-S5, EF-STK-06).

    Écart validé (Q-O, dette v0.2) : unicité (magasin, article)
    ``uq_seuil_stock_magasin_article``. RG-S5 dit « deux seuils par article et
    par magasin » ; sans unicité, le stock courant (identifié par le seuil)
    pourrait se dédoubler.
    """

    id_seuil = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seuil_minimal = _quantite(default=Decimal("0"))
    seuil_critique = _quantite(default=Decimal("0"))
    # Un seuil inactif n'émet pas d'alerte de seuil ; le serveur en crée un
    # au premier mouvement d'un article dans un magasin (Q-O).
    actif = models.BooleanField(default=False)
    magasin = models.ForeignKey(
        Magasin,
        on_delete=models.PROTECT,
        db_column="magasin_id_magasin",
        db_index=False,
        related_name="seuils_stock",
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.PROTECT,
        db_column="article_id_article",
        db_index=False,
        related_name="seuils_stock",
    )

    class Meta:
        db_table = "seuil_stock"
        verbose_name = "seuil de stock"
        constraints = [
            models.UniqueConstraint(
                fields=["magasin", "article"], name="uq_seuil_stock_magasin_article"
            ),
        ]
        indexes = [
            models.Index(fields=["magasin"], name="ix_seuil_stock_magasin_id_magasin"),
            models.Index(fields=["article"], name="ix_seuil_stock_article_id_article"),
        ]

    def __str__(self) -> str:
        return f"seuil {self.article_id} / {self.magasin_id}"


class StockCourant(models.Model):
    """Projection du stock d'un article dans un magasin (CL-4
    ``StockCourant``). RG-S2 : c'est la somme des mouvements ; elle n'est
    jamais saisie, seulement recalculée par le service des mouvements.

    Identification relative par le seuil (MLD § 6.4) : la clé primaire est
    ``seuil_stock_id_seuil``.
    """

    seuil_stock = models.OneToOneField(
        SeuilStock,
        on_delete=models.PROTECT,
        primary_key=True,
        db_column="seuil_stock_id_seuil",
        related_name="stock_courant",
    )
    quantite = _quantite(default=Decimal("0"))
    date_calcul = models.DateTimeField(default=timezone.now)
    niveau_alerte = models.CharField(max_length=32, default=NIVEAU_NORMAL)

    class Meta:
        db_table = "stock_courant"
        verbose_name = "stock courant"
        constraints = [
            models.CheckConstraint(
                condition=Q(niveau_alerte__in=NIVEAUX), name="ck_stock_courant_niveau_alerte"
            ),
        ]
        indexes = [
            models.Index(
                fields=["niveau_alerte"],
                name="ix_stock_courant_alerte",
                condition=~Q(niveau_alerte=NIVEAU_NORMAL),
            ),
        ]

    def __str__(self) -> str:
        return f"{self.quantite} ({self.niveau_alerte})"


class Alerte(models.Model):
    """Alerte de stock (CL-4 ``Alerte``, RG-S5, RG-S7, EF-STK-07), distincte
    des alertes techniques d'exploitation (socle/alertes.py)."""

    id_alerte = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_alerte = models.CharField(max_length=32)
    niveau = models.CharField(max_length=32)
    message = models.TextField()
    date_emission = models.DateTimeField(default=timezone.now)
    statut = models.CharField(max_length=32)
    stock_courant = models.ForeignKey(
        StockCourant,
        on_delete=models.PROTECT,
        db_column="stock_courant_seuil_stock_id_seuil",
        db_index=False,
        related_name="alertes",
    )

    class Meta:
        db_table = "alerte"
        verbose_name = "alerte de stock"
        constraints = [
            models.CheckConstraint(
                condition=Q(type_alerte__in=TYPES_ALERTE), name="ck_alerte_type_alerte"
            ),
            models.CheckConstraint(condition=Q(niveau__in=NIVEAUX), name="ck_alerte_niveau"),
            models.CheckConstraint(condition=Q(statut__in=STATUTS_ALERTE), name="ck_alerte_statut"),
        ]
        indexes = [
            models.Index(
                fields=["stock_courant"], name="ix_alerte_stock_courant_seuil_stock_id_seuil"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.type_alerte} · {self.statut}"


class Inventaire(models.Model):
    """Inventaire contradictoire d'un magasin (CL-4 ``Inventaire``, SQ-4,
    EF-STK-08)."""

    id_inventaire = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_debut = models.DateField(default=timezone.localdate)
    date_fin = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=32, default=INVENTAIRE_EN_COURS)
    magasin = models.ForeignKey(
        Magasin,
        on_delete=models.PROTECT,
        db_column="magasin_id_magasin",
        db_index=False,
        related_name="inventaires",
    )

    class Meta:
        db_table = "inventaire"
        verbose_name = "inventaire"
        constraints = [
            models.CheckConstraint(
                condition=Q(statut__in=STATUTS_INVENTAIRE), name="ck_inventaire_statut"
            ),
        ]
        indexes = [
            models.Index(fields=["magasin"], name="ix_inventaire_magasin_id_magasin"),
        ]

    def __str__(self) -> str:
        return f"inventaire du {self.date_debut} ({self.statut})"


class LigneInventaire(models.Model):
    """Une ligne de comptage (CL-4 ``LigneInventaire``) : quantité théorique
    figée à l'ouverture, quantité comptée, écart (compté − théorique, RG-S9)."""

    id_ligne = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quantite_theorique = _quantite()
    quantite_comptee = _quantite(null=True, blank=True)
    ecart = _quantite(null=True, blank=True)
    statut = models.CharField(max_length=32, default=LIGNE_A_COMPTER)
    inventaire = models.ForeignKey(
        Inventaire,
        on_delete=models.PROTECT,
        db_column="inventaire_id_inventaire",
        db_index=False,
        related_name="lignes",
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.PROTECT,
        db_column="article_id_article",
        db_index=False,
        related_name="lignes_inventaire",
    )

    class Meta:
        db_table = "ligne_inventaire"
        verbose_name = "ligne d'inventaire"
        constraints = [
            models.CheckConstraint(
                condition=Q(statut__in=STATUTS_LIGNE), name="ck_ligne_inventaire_statut"
            ),
        ]
        indexes = [
            models.Index(
                fields=["inventaire"], name="ix_ligne_inventaire_inventaire_id_inventaire"
            ),
            models.Index(fields=["article"], name="ix_ligne_inventaire_article_id_article"),
        ]

    def __str__(self) -> str:
        return f"ligne {self.article_id} ({self.statut})"


class MouvementStock(models.Model):
    """Mouvement du journal de stock immuable (CL-4 ``MouvementStock``,
    RG-S2, RG-S8). Il ne se modifie ni ne se supprime : une erreur se corrige
    par un contre-mouvement justifié (EF-STK-11).

    ``uuid`` est fourni par le client quand il existe (téléphone hors ligne) :
    il rend l'envoi idempotent (exigence 6.4, ET-3 « déjà reçu »).

    ``statut_validation`` est écrit une seule fois, à l'insertion
    (Q-K, I-13) ; le statut servi par l'API est dérivé des événements.

    Écarts validés (Q-L, 2026-11-22, dette v0.2), réclamés par RG-S1, RG-S3,
    RG-S4, RG-S8 et par les deux fronts :
      * ``motif`` — obligatoire pour une perte, un ajustement, un
        contre-mouvement (RG-S3, RG-S8) ;
      * ``beneficiaire`` et ``corps_etat_code_corps_etat`` — destination
        complète d'une sortie (RG-S4) ;
      * ``unite_mesure_code_unite`` — unité de la quantité saisie, sans
        laquelle ``quantite_base`` ne peut pas être recalculée (RG-S1) ;
      * ``mouvement_annule_uuid`` — mouvement corrigé par ce contre-mouvement
        (ET-2 « annulé par contre-mouvement »), unique : un mouvement ne
        s'annule qu'une fois ;
      * CHECK ``ck_mouvement_stock_quantites_positives`` — RG-S4 « quantité > 0 »
        (le sens vient du type de mouvement).
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quantite_saisie = _quantite()
    quantite_base = _quantite()
    date_operation = models.DateTimeField(default=timezone.now)
    horodatage_appareil = models.DateTimeField(default=timezone.now)
    horodatage_serveur = models.DateTimeField(default=timezone.now)
    statut_validation = models.CharField(max_length=32, default=STATUT_ENREGISTRE)
    reference_externe = models.CharField(max_length=120, null=True, blank=True)  # noqa: DJ001
    motif = models.TextField(null=True, blank=True)  # noqa: DJ001
    beneficiaire = models.CharField(max_length=120, null=True, blank=True)  # noqa: DJ001
    type_mouvement = models.ForeignKey(
        TypeMouvement,
        on_delete=models.PROTECT,
        db_column="type_mouvement_code_type_mouvement",
        db_index=False,
        related_name="mouvements",
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.PROTECT,
        db_column="article_id_article",
        db_index=False,
        related_name="mouvements",
    )
    magasin = models.ForeignKey(
        Magasin,
        on_delete=models.PROTECT,
        db_column="magasin_id_magasin",
        db_index=False,
        related_name="mouvements",
    )
    logement = models.ForeignKey(
        Logement,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="logement_id_logement",
        db_index=False,
        related_name="mouvements",
    )
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column="utilisateur_id_utilisateur",
        db_index=False,
        related_name="mouvements",
    )
    stock_courant = models.ForeignKey(
        StockCourant,
        on_delete=models.PROTECT,
        db_column="stock_courant_seuil_stock_id_seuil",
        db_index=False,
        related_name="mouvements",
    )
    ligne_inventaire = models.ForeignKey(
        LigneInventaire,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="ligne_inventaire_id_ligne",
        db_index=False,
        related_name="ajustements",
    )
    corps_etat = models.ForeignKey(
        CorpsEtat,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="corps_etat_code_corps_etat",
        db_index=False,
        related_name="mouvements",
    )
    unite_mesure = models.ForeignKey(
        UniteMesure,
        on_delete=models.PROTECT,
        db_column="unite_mesure_code_unite",
        db_index=False,
        related_name="mouvements",
    )
    mouvement_annule = models.OneToOneField(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="mouvement_annule_uuid",
        related_name="contre_mouvement",
    )

    # Écart Q-BD (I-51, dette v0.2) : appareil et version de l'application
    # de la saisie mobile (traçabilité, cahier des charges § 9) ; vides pour
    # une saisie web. La version est recopiée : celle de l'appareil change.
    appareil = models.ForeignKey(
        "identite.Appareil",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="appareil_id_appareil",
        db_index=False,
        related_name="+",
    )
    version_application = models.CharField(max_length=120, null=True, blank=True)  # noqa: DJ001

    class Meta:
        db_table = "mouvement_stock"
        verbose_name = "mouvement de stock"
        constraints = [
            models.CheckConstraint(
                condition=Q(statut_validation__in=STATUTS_VALIDATION),
                name="ck_mouvement_stock_statut_validation",
            ),
            models.CheckConstraint(
                condition=Q(quantite_saisie__gt=0, quantite_base__gt=0),
                name="ck_mouvement_stock_quantites_positives",
            ),
        ]
        indexes = [
            models.Index(
                fields=["type_mouvement"],
                name="ix_mouvement_stock_type_mouvement_code_type_mouvement",
            ),
            models.Index(fields=["article"], name="ix_mouvement_stock_article_id_article"),
            models.Index(fields=["magasin"], name="ix_mouvement_stock_magasin_id_magasin"),
            models.Index(fields=["logement"], name="ix_mouvement_stock_logement_id_logement"),
            models.Index(
                fields=["utilisateur"], name="ix_mouvement_stock_utilisateur_id_utilisateur"
            ),
            models.Index(
                fields=["stock_courant"],
                name="ix_mouvement_stock_stock_courant_seuil_stock_id_seuil",
            ),
            models.Index(
                fields=["ligne_inventaire"], name="ix_mouvement_stock_ligne_inventaire_id_ligne"
            ),
            models.Index(
                fields=["statut_validation", "date_operation"],
                name="ix_mouvement_stock_a_valider",
                condition=Q(statut_validation=STATUT_A_VALIDER),
            ),
            # Écart Q-L : index des nouvelles clés étrangères (MPD § 6.5 :
            # toute clé étrangère hors clé primaire est indexée).
            models.Index(
                fields=["corps_etat"], name="ix_mouvement_stock_corps_etat_code_corps_etat"
            ),
            models.Index(
                fields=["unite_mesure"], name="ix_mouvement_stock_unite_mesure_code_unite"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.type_mouvement_id} · {self.quantite_base}"


class EvenementValidation(models.Model):
    """Décision sur un mouvement (CL-4 ``EvenementValidation``, RG-S6,
    RG-D8, RG-D11). Immuable et partitionnée par mois sur
    ``horodatage_serveur`` (MPD-4) ; table créée en SQL (migration stock
    0002), d'où la clé primaire composite imposée par PostgreSQL.

    Idempotence (I-17) : la clé primaire comprend l'horodatage, donc
    ``uuid`` seul n'est pas unique en base ; le service vérifie qu'un
    événement de même ``uuid`` n'existe pas avant d'écrire.
    """

    pk = models.CompositePrimaryKey("uuid", "horodatage_serveur")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    type_objet = models.CharField(max_length=120)
    decision = models.CharField(max_length=32)
    motif = models.TextField(null=True, blank=True)  # noqa: DJ001
    horodatage_serveur = models.DateTimeField(default=timezone.now)
    mouvement_stock = models.ForeignKey(
        MouvementStock,
        on_delete=models.PROTECT,
        db_column="mouvement_stock_uuid",
        db_index=False,
        related_name="evenements_validation",
    )
    regle_validation = models.ForeignKey(
        RegleValidation,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="regle_validation_id_regle",
        db_index=False,
        related_name="evenements_validation",
    )
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column="utilisateur_id_utilisateur",
        db_index=False,
        related_name="evenements_validation",
    )

    # Écart Q-BD (I-51, dette v0.2) : appareil et version de l'application
    # de la saisie mobile (traçabilité, cahier des charges § 9) ; vides pour
    # une saisie web. La version est recopiée : celle de l'appareil change.
    appareil = models.ForeignKey(
        "identite.Appareil",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="appareil_id_appareil",
        db_index=False,
        related_name="+",
    )
    version_application = models.CharField(max_length=120, null=True, blank=True)  # noqa: DJ001

    class Meta:
        db_table = "evenement_validation"
        verbose_name = "événement de validation"
        constraints = [
            models.CheckConstraint(
                condition=Q(decision__in=DECISIONS), name="ck_evenement_validation_decision"
            ),
        ]
        indexes = [
            models.Index(
                fields=["mouvement_stock"], name="ix_evenement_validation_mouvement_stock_uuid"
            ),
            models.Index(
                fields=["regle_validation"],
                name="ix_evenement_validation_regle_validation_id_regle",
            ),
            models.Index(
                fields=["utilisateur"], name="ix_evenement_validation_utilisateur_id_utilisateur"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.decision} · {self.mouvement_stock_id}"
