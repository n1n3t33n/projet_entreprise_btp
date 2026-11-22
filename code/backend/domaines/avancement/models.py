"""Modèles du MPD-5, partie avancement (les notifications arrivent en B6).

Noms repris exactement du MPD-5. Nullité des clés étrangères tirée du MCD
(règle Q-B : (1,1) → NOT NULL, (0,1) → NULL) :
  etape_travaux        « suivi par »       logement          (1,1) → NOT NULL
  etape_travaux        « instanciée en »   etape_modele      (1,1) → NOT NULL
  fiche_route          « établie pour »    utilisateur       (1,1) → NOT NULL
  evenement_execution  « historisée par »  etape_travaux     (1,1) → NOT NULL
  evenement_execution  « déclaré par »     utilisateur       (1,1) → NOT NULL
  evenement_execution  « motive »          motif_blocage     (0,1) → NULL
  evenement_execution  « manquant dans »   article           (0,1) → NULL
  evenement_execution  « alimente »        avancement_agrege (1,1) → NOT NULL :
      l'agrégat de SON logement, unité de suivi (H11, arbitrage Q-V)
  ligne_fiche_route    association « regrouper » : clé (fiche, étape)

``evenement_execution`` est immuable (RG-A5, RG-S8) et partitionnée par mois
sur ``horodatage_serveur`` (Q-U, I-16 : l'heure du téléphone peut être fausse
ou très en retard) ; elle est créée en SQL par la migration ``avancement
0002``. Les autres tables changent : ``etape_travaux`` porte le statut
courant, projection des événements, comme ``stock_courant`` pour le stock.
"""

import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from domaines.avancement.constantes import (
    A_FAIRE,
    FICHE_OUVERTE,
    PORTEES,
    STATUTS_ETAPE,
    STATUTS_FICHE,
    TYPES_CYCLE,
)
from domaines.organisation.models import Logement
from domaines.referentiels.models import Article, EtapeModele, MotifBlocage


def _quantite(**options: object) -> models.DecimalField:  # type: ignore[type-arg]
    return models.DecimalField(max_digits=14, decimal_places=3, **options)  # type: ignore[arg-type]


class EtapeTravaux(models.Model):
    """Étape d'un logement, instanciée depuis la gamme de son type (CL-5
    ``EtapeTravaux``, RG-A1, EF-AVA-01).

    Écart validé (Q-AA, dette v0.2) : unicité (logement, étape modèle)
    ``uq_etape_travaux_logement_etape_modele`` — une étape modèle ne
    s'instancie qu'une fois par logement ; la génération est ainsi rejouable.
    """

    id_etape = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    statut = models.CharField(max_length=32, default=A_FAIRE)
    date_prevue = models.DateField(null=True, blank=True)
    date_fin_declaree = models.DateField(null=True, blank=True)
    date_validation = models.DateTimeField(null=True, blank=True)
    # Poids copié de l'étape modèle à l'instanciation : une nouvelle version
    # de gamme ne change pas l'avancement des logements déjà suivis.
    poids_effectif = _quantite(default=Decimal("0"))
    logement = models.ForeignKey(
        Logement,
        on_delete=models.PROTECT,
        db_column="logement_id_logement",
        db_index=False,
        related_name="etapes_travaux",
    )
    etape_modele = models.ForeignKey(
        EtapeModele,
        on_delete=models.PROTECT,
        db_column="etape_modele_id_etape_modele",
        db_index=False,
        related_name="etapes_travaux",
    )

    class Meta:
        db_table = "etape_travaux"
        verbose_name = "étape de travaux"
        constraints = [
            models.CheckConstraint(
                condition=Q(statut__in=STATUTS_ETAPE), name="ck_etape_travaux_statut"
            ),
            models.UniqueConstraint(
                fields=["logement", "etape_modele"], name="uq_etape_travaux_logement_etape_modele"
            ),
        ]
        indexes = [
            models.Index(fields=["logement"], name="ix_etape_travaux_logement_id_logement"),
            models.Index(
                fields=["etape_modele"], name="ix_etape_travaux_etape_modele_id_etape_modele"
            ),
            models.Index(fields=["statut", "date_prevue"], name="ix_etape_travaux_statut"),
        ]

    def __str__(self) -> str:
        return f"{self.etape_modele_id} · {self.statut}"


class FicheRoute(models.Model):
    """Fiche de route d'un technicien pour un cycle de travail (CL-5
    ``FicheRoute``, RG-A7, AC-3). ``date_fin`` est nulle pour un cycle
    « logement », qui se clôture quand son travail est fait."""

    id_fiche = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_cycle = models.CharField(max_length=32)
    date_debut = models.DateField(default=timezone.localdate)
    date_fin = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=32, default=FICHE_OUVERTE)
    date_cloture = models.DateTimeField(null=True, blank=True)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column="utilisateur_id_utilisateur",
        db_index=False,
        related_name="fiches_route",
    )

    class Meta:
        db_table = "fiche_route"
        verbose_name = "fiche de route"
        constraints = [
            models.CheckConstraint(
                condition=Q(type_cycle__in=TYPES_CYCLE), name="ck_fiche_route_type_cycle"
            ),
            models.CheckConstraint(
                condition=Q(statut__in=STATUTS_FICHE), name="ck_fiche_route_statut"
            ),
        ]
        indexes = [
            models.Index(fields=["utilisateur"], name="ix_fiche_route_utilisateur_id_utilisateur"),
        ]

    def __str__(self) -> str:
        return f"fiche du {self.date_debut} ({self.statut})"


class LigneFicheRoute(models.Model):
    """Étape inscrite sur une fiche de route (association MCD « regrouper »,
    CL-5 ``LigneFicheRoute``). Clé primaire composite (fiche, étape) soulignée
    au MPD-5 ; ``id_ligne`` y figure sans être clé."""

    pk = models.CompositePrimaryKey("fiche_route_id", "etape_travaux_id")
    fiche_route = models.ForeignKey(
        FicheRoute,
        on_delete=models.PROTECT,
        db_column="fiche_route_id_fiche",
        related_name="lignes",
    )
    etape_travaux = models.ForeignKey(
        EtapeTravaux,
        on_delete=models.PROTECT,
        db_column="etape_travaux_id_etape",
        related_name="lignes_fiche",
    )
    id_ligne = models.UUIDField(default=uuid.uuid4, editable=False)
    ordre = models.IntegerField(default=0)
    reportee = models.BooleanField(default=False)
    motif_report = models.TextField(null=True, blank=True)  # noqa: DJ001

    class Meta:
        db_table = "ligne_fiche_route"
        verbose_name = "ligne de fiche de route"

    def __str__(self) -> str:
        return f"ligne {self.ordre}"


class AvancementAgrege(models.Model):
    """Avancement déclaré et validé d'une portée (CL-5 ``AvancementAgrege``,
    RG-A6) : logement, zone, chantier ou corps d'état d'un chantier.

    Écart validé (Q-V, dette v0.2) : ``id_cible`` — identifiant de ce qui est
    agrégé (logement, zone, chantier, ou « chantier:code du corps d'état ») ;
    le MLD reconnaît qu'aucun lien vers la portée n'existe (§ 6.4) et le web
    l'attend (``AvancementAgregeDto.id_cible``). Unique avec la portée.
    """

    id_avancement = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portee = models.CharField(max_length=32)
    id_cible = models.CharField(max_length=120)
    pourcentage_declare = _quantite(default=Decimal("0"))
    pourcentage_valide = _quantite(default=Decimal("0"))
    nombre_etapes = models.IntegerField(default=0)
    date_calcul = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "avancement_agrege"
        verbose_name = "avancement agrégé"
        constraints = [
            models.CheckConstraint(
                condition=Q(portee__in=PORTEES), name="ck_avancement_agrege_portee"
            ),
            models.UniqueConstraint(
                fields=["portee", "id_cible"], name="uq_avancement_agrege_portee_id_cible"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.portee} {self.id_cible} : {self.pourcentage_valide} %"


class EvenementExecution(models.Model):
    """Changement de statut d'une étape (CL-5 ``EvenementExecution``, RG-A5) :
    qui, quand (appareil et serveur), pour le compte de qui, avant, après,
    motif. Immuable, partitionnée par mois ; table créée en SQL (migration
    avancement 0002), d'où la clé primaire composite.

    Écart validé (Q-W, dette v0.2) : ``pour_le_compte_de_id_utilisateur`` —
    technicien pour qui la déclaration est faite (RG-A9, délégation). Figé à
    l'écriture : le déduire de la fiche de route actuelle fausserait
    l'historique après une réaffectation. NULL quand l'auteur déclare pour
    lui-même ou pour une opération qui n'est pas une déclaration.
    """

    pk = models.CompositePrimaryKey("uuid", "horodatage_serveur")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    statut_avant = models.CharField(max_length=32, null=True, blank=True)  # noqa: DJ001
    statut_apres = models.CharField(max_length=32)
    horodatage_appareil = models.DateTimeField(default=timezone.now)
    horodatage_serveur = models.DateTimeField(default=timezone.now)
    commentaire = models.CharField(max_length=120, null=True, blank=True)  # noqa: DJ001
    etape_travaux = models.ForeignKey(
        EtapeTravaux,
        on_delete=models.PROTECT,
        db_column="etape_travaux_id_etape",
        db_index=False,
        related_name="evenements",
    )
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column="utilisateur_id_utilisateur",
        db_index=False,
        related_name="evenements_execution",
    )
    pour_le_compte_de = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="pour_le_compte_de_id_utilisateur",
        db_index=False,
        related_name="evenements_delegues",
    )
    motif_blocage = models.ForeignKey(
        MotifBlocage,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="motif_blocage_code_motif",
        db_index=False,
        related_name="evenements_execution",
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="article_id_article",
        db_index=False,
        related_name="evenements_execution",
    )
    avancement_agrege = models.ForeignKey(
        AvancementAgrege,
        on_delete=models.PROTECT,
        db_column="avancement_agrege_id_avancement",
        db_index=False,
        related_name="evenements",
    )

    class Meta:
        db_table = "evenement_execution"
        verbose_name = "événement d'exécution"
        constraints = [
            models.CheckConstraint(
                condition=Q(statut_avant__in=STATUTS_ETAPE) | Q(statut_avant__isnull=True),
                name="ck_evenement_execution_statut_avant",
            ),
            models.CheckConstraint(
                condition=Q(statut_apres__in=STATUTS_ETAPE),
                name="ck_evenement_execution_statut_apres",
            ),
        ]
        indexes = [
            models.Index(
                fields=["etape_travaux"], name="ix_evenement_execution_etape_travaux_id_etape"
            ),
            models.Index(
                fields=["utilisateur"], name="ix_evenement_execution_utilisateur_id_utilisateur"
            ),
            models.Index(
                fields=["motif_blocage"], name="ix_evenement_execution_motif_blocage_code_motif"
            ),
            models.Index(fields=["article"], name="ix_evenement_execution_article_id_article"),
            models.Index(
                fields=["avancement_agrege"],
                name="ix_evenement_execution_avancement_agrege_id_avancement",
            ),
            # Écart Q-W : index de la nouvelle clé étrangère (MPD § 6.5).
            models.Index(
                fields=["pour_le_compte_de"],
                name="ix_evenement_execution_pour_le_compte_de_id_utilisateur",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.statut_avant} → {self.statut_apres}"
