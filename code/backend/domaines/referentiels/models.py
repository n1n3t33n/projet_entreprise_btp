"""Modèles du MPD-3 (référentiels et catalogue).

Ce sont des TABLES et non des énumérations : types de mouvement, motifs de
blocage, règles de validation, unités et familles vivent en base et se
règlent sans redéploiement (« données en base et non du code », MPD § 6.5).

Noms repris exactement du MPD-3. Nullité des clés étrangères tirée du MCD-3
(règle validée le 2026-11-18, I-32) :
  article      « classe »          categorie_article (0,1) → NULL
  article      « unité de base de » unite_mesure      (1,1) → NOT NULL
  gamme        « défini par »      type_logement     (1,1) → NOT NULL
  etape_modele « composée de »     gamme             (1,1) → NOT NULL
  etape_modele « relève de »       corps_etat        (1,1) → NOT NULL
Les quantités sont en numeric(14,3), jamais en flottant (MPD § 6.5).
"""

import uuid

from django.db import models
from django.db.models import Q

from domaines.organisation.models import TypeLogement
from domaines.referentiels.constantes import (
    ORIGINES_ARTICLE,
    STATUT_GAMME_BROUILLON,
    STATUTS_GAMME,
    TYPES_UNITE,
)


def _quantite(**options: object) -> models.DecimalField:  # type: ignore[type-arg]
    """numeric(14,3) : précision des quantités et des poids (MPD § 6.5)."""
    return models.DecimalField(max_digits=14, decimal_places=3, **options)  # type: ignore[arg-type]


class CategorieArticle(models.Model):
    """Famille d'articles (CL-3a ``CategorieArticle``, MPD-3).

    Plate, comme au MPD (arbitrage Q-E) : pas de famille parente. L'API rend
    ``code_parent: null`` au module Stock du web, qui aplatira son arborescence
    (F-11) ; une hiérarchie ne sera ajoutée qu'en v0.2 si le métier la confirme.
    """

    code_categorie = models.CharField(primary_key=True, max_length=32)
    libelle = models.CharField(max_length=120)

    class Meta:
        db_table = "categorie_article"
        verbose_name = "famille d'articles"

    def __str__(self) -> str:
        return self.libelle


class UniteMesure(models.Model):
    """Unité de mesure (CL-3a ``UniteMesure``, MPD-3)."""

    code_unite = models.CharField(primary_key=True, max_length=32)
    libelle = models.CharField(max_length=120)
    type_unite = models.CharField(max_length=32)

    class Meta:
        db_table = "unite_mesure"
        verbose_name = "unité de mesure"
        constraints = [
            models.CheckConstraint(
                condition=Q(type_unite__in=TYPES_UNITE), name="ck_unite_mesure_type_unite"
            ),
        ]

    def __str__(self) -> str:
        return self.libelle


class Article(models.Model):
    """Article du catalogue (CL-3a ``Article``, MPD-3).

    Code et code-barres uniques (``uq_article_code``, ``uq_article_code_barre``) :
    la lecture d'un code-barres sur le téléphone retrouve un seul article.
    """

    id_article = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=32)
    designation = models.CharField(max_length=120)
    origine = models.CharField(max_length=32)
    # NULL voulu : un article sans code-barres n'en a pas (une chaîne vide
    # violerait l'unicité dès le deuxième article sans code-barres).
    code_barre = models.CharField(max_length=32, null=True, blank=True)  # noqa: DJ001
    actif = models.BooleanField(default=True)
    categorie_article = models.ForeignKey(
        CategorieArticle,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column="categorie_article_code_categorie",
        db_index=False,
        related_name="articles",
    )
    unite_mesure = models.ForeignKey(
        UniteMesure,
        on_delete=models.PROTECT,
        db_column="unite_mesure_code_unite",
        db_index=False,
        related_name="articles",
    )

    class Meta:
        db_table = "article"
        verbose_name = "article"
        constraints = [
            models.UniqueConstraint(fields=["code"], name="uq_article_code"),
            models.UniqueConstraint(fields=["code_barre"], name="uq_article_code_barre"),
            models.CheckConstraint(
                condition=Q(origine__in=ORIGINES_ARTICLE), name="ck_article_origine"
            ),
        ]
        indexes = [
            models.Index(
                fields=["categorie_article"], name="ix_article_categorie_article_code_categorie"
            ),
            models.Index(fields=["unite_mesure"], name="ix_article_unite_mesure_code_unite"),
        ]

    def __str__(self) -> str:
        return self.designation


class Conditionnement(models.Model):
    """Conditionnement d'un article dans une unité (CL-3a ``Conditionnement``,
    association MCD « conditionner », MPD-3) : 1 sac = 50 kg, par exemple.

    Clé primaire composite (article, unité) soulignée au MPD-3 : non
    enregistrable dans l'admin de Django 5.2 (I-15), géré par l'API.
    """

    pk = models.CompositePrimaryKey("article_id", "unite_mesure_id")
    article = models.ForeignKey(
        Article,
        on_delete=models.PROTECT,
        db_column="article_id_article",
        db_index=False,
        related_name="conditionnements",
    )
    unite_mesure = models.ForeignKey(
        UniteMesure,
        on_delete=models.PROTECT,
        db_column="unite_mesure_code_unite",
        db_index=False,
        related_name="conditionnements",
    )
    id_conditionnement = models.UUIDField(default=uuid.uuid4, editable=False)
    facteur_conversion = _quantite()

    class Meta:
        db_table = "conditionnement"
        verbose_name = "conditionnement"

    def __str__(self) -> str:
        return f"{self.article_id} · {self.unite_mesure_id}"


class CorpsEtat(models.Model):
    """Corps d'état (gros œuvre, électricité…), CL-3b ``CorpsEtat``, MPD-3."""

    code_corps_etat = models.CharField(primary_key=True, max_length=32)
    libelle = models.CharField(max_length=120)
    ordre = models.IntegerField()
    couleur = models.CharField(max_length=120)

    class Meta:
        db_table = "corps_etat"
        verbose_name = "corps d'état"

    def __str__(self) -> str:
        return self.libelle


class Gamme(models.Model):
    """Version de gamme de travaux d'un type de logement (CL-3b ``Gamme``,
    MPD-3 ; EF-REF-05, EF-REF-09 « publier une version de gamme »).

    La gamme référence le domaine « organisation » (type de logement) : c'est
    le sens du graphe des dépendances (référentiels → organisation).
    """

    id_gamme = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.IntegerField()
    libelle = models.CharField(max_length=120)
    statut = models.CharField(max_length=32, default=STATUT_GAMME_BROUILLON)
    date_activation = models.DateTimeField(null=True, blank=True)
    type_logement = models.ForeignKey(
        TypeLogement,
        on_delete=models.PROTECT,
        db_column="type_logement_code_type",
        db_index=False,
        related_name="gammes",
    )

    class Meta:
        db_table = "gamme"
        verbose_name = "gamme"
        constraints = [
            models.CheckConstraint(condition=Q(statut__in=STATUTS_GAMME), name="ck_gamme_statut"),
        ]
        indexes = [
            models.Index(fields=["type_logement"], name="ix_gamme_type_logement_code_type"),
        ]

    def __str__(self) -> str:
        return f"{self.libelle} (v{self.version})"


class EtapeModele(models.Model):
    """Étape type d'une gamme (CL-3b ``EtapeModele``, MPD-3) : modèle à partir
    duquel les étapes de travaux d'un logement sont instanciées (MCD
    « instanciée en », B4). ``poids`` sert au calcul de l'avancement (RG-A6).
    """

    id_etape_modele = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=32)
    libelle = models.CharField(max_length=120)
    ordre = models.IntegerField()
    poids = _quantite()
    controle_requis = models.BooleanField(default=False)
    gamme = models.ForeignKey(
        Gamme,
        on_delete=models.PROTECT,
        db_column="gamme_id_gamme",
        db_index=False,
        related_name="etapes",
    )
    corps_etat = models.ForeignKey(
        CorpsEtat,
        on_delete=models.PROTECT,
        db_column="corps_etat_code_corps_etat",
        db_index=False,
        related_name="etapes_modeles",
    )

    class Meta:
        db_table = "etape_modele"
        verbose_name = "étape modèle"
        constraints = [
            # MPD-3 : code unique sur tout le catalogue, toutes versions de
            # gamme confondues (I-36 : une nouvelle version reçoit donc des
            # codes d'étape propres).
            models.UniqueConstraint(fields=["code"], name="uq_etape_modele_code"),
        ]
        indexes = [
            models.Index(fields=["gamme"], name="ix_etape_modele_gamme_id_gamme"),
            models.Index(fields=["corps_etat"], name="ix_etape_modele_corps_etat_code_corps_etat"),
        ]

    def __str__(self) -> str:
        return self.libelle


class TypeMouvement(models.Model):
    """Type de mouvement de stock (CL-3a ``TypeMouvement``, MPD-3) : codes
    partagés avec les fronts (ENT_RECEPTION, SOR_LOGEMENT, RET_RETOUR,
    SOR_PERTE). ``sens`` vaut +1 (entrée) ou -1 (sortie) ; le MPD n'impose
    aucun CHECK, on n'en crée pas."""

    code_type_mouvement = models.CharField(primary_key=True, max_length=32)
    libelle = models.CharField(max_length=120)
    sens = models.IntegerField()
    motif_obligatoire = models.BooleanField(default=False)
    destination_obligatoire = models.BooleanField(default=False)

    class Meta:
        db_table = "type_mouvement"
        verbose_name = "type de mouvement"

    def __str__(self) -> str:
        return self.libelle


class MotifBlocage(models.Model):
    """Motif de blocage d'une étape (CL-3b ``MotifBlocage``, MPD-3).
    ``requiert_article`` : « manque de matériel » oblige à désigner l'article
    manquant (RG-A10)."""

    code_motif = models.CharField(primary_key=True, max_length=32)
    libelle = models.CharField(max_length=120)
    requiert_article = models.BooleanField(default=False)
    actif = models.BooleanField(default=True)

    class Meta:
        db_table = "motif_blocage"
        verbose_name = "motif de blocage"

    def __str__(self) -> str:
        return self.libelle


class RegleValidation(models.Model):
    """Règle de validation (CL-3a ``RegleValidation``, MPD-3 ; EF-REF-08
    « définir les règles de validation »).

    Une règle dit quand un événement doit passer par un valideur (RG-S6) :
    type d'événement, champ testé, opérateur, seuil, délai. Le MPD laisse
    ``type_evenement`` et ``operateur`` libres (pas de CHECK) : l'API contrôle
    leurs valeurs (constantes.py). La règle n'est rattachée à aucun chantier
    au MPD : elle vaut pour tout le programme. ``delai_heures`` n'est qu'un
    REPLI pour la relance (décision Q-F) : le paramètre de chantier l'emporte.
    """

    id_regle = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_evenement = models.CharField(max_length=120)
    champ_teste = models.CharField(max_length=120)
    operateur = models.CharField(max_length=120)
    valeur_seuil = _quantite(null=True, blank=True)
    delai_heures = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "regle_validation"
        verbose_name = "règle de validation"

    def __str__(self) -> str:
        return f"{self.type_evenement} · {self.champ_teste} {self.operateur}"
