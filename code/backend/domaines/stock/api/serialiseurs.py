"""Sérialiseurs du domaine « stock » : ils fixent le CONTRAT d'API.

Formes reprises de ``features/stock/api/dto.ts`` (web) : ``LigneStockDto``,
``MouvementStockDto``, ``NoeudStock``. Quantités en chaîne (numeric(14,3)).
Ajouts compatibles : ``code_unite``, ``corps_etat``, ``beneficiaire``,
``horodatage_appareil``, ``mouvement_annule_uuid`` (écarts Q-L) et
``derive_horloge`` (RG-S11). Les routes de validation et d'inventaire n'ont
pas encore d'écran web : leur forme est définie ici (contrat d'abord, F-12).
"""

from datetime import timedelta
from decimal import Decimal
from typing import Any

from rest_framework import serializers

from domaines.organisation import selecteurs as selecteurs_organisation
from domaines.referentiels import selecteurs as selecteurs_referentiels
from domaines.stock import selecteurs
from domaines.stock.constantes import DECISIONS
from domaines.stock.models import Alerte, MouvementStock, SeuilStock


def _quantite(**options: Any) -> serializers.DecimalField:
    return serializers.DecimalField(max_digits=14, decimal_places=3, **options)


# --- Lignes de stock --------------------------------------------------------------
class UniteBaseSerializer(serializers.Serializer):  # type: ignore[type-arg]
    code_unite = serializers.CharField()
    libelle = serializers.CharField()
    type_unite = serializers.CharField()


class ArticleStockSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """``ArticleDto`` de l'écran Stock : unité de base imbriquée (I-30)."""

    id_article = serializers.UUIDField()
    code = serializers.CharField()
    designation = serializers.CharField()
    origine = serializers.CharField()
    code_barre = serializers.CharField(allow_null=True)
    actif = serializers.BooleanField()
    unite_base = UniteBaseSerializer(source="unite_mesure")
    code_categorie = serializers.CharField(source="categorie_article_id", allow_null=True)


class SeuilSerializer(serializers.Serializer):  # type: ignore[type-arg]
    id_seuil = serializers.UUIDField()
    seuil_minimal = _quantite()
    seuil_critique = _quantite()
    actif = serializers.BooleanField()


class EtatStockSerializer(serializers.Serializer):  # type: ignore[type-arg]
    quantite = _quantite()
    date_calcul = serializers.DateTimeField()
    niveau_alerte = serializers.CharField()


class LigneStockSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """``LigneStockDto`` : l'article, ses seuils et son stock courant."""

    article = ArticleStockSerializer()
    libelle_famille = serializers.SerializerMethodField()
    seuil = SeuilSerializer(source="*")
    stock = EtatStockSerializer(source="stock_courant")

    def get_libelle_famille(self, obj: SeuilStock) -> str:
        famille = obj.article.categorie_article
        return famille.libelle if famille else ""


class SeuilEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    seuil_minimal = _quantite(min_value=0)
    seuil_critique = _quantite(min_value=0)


class NoeudStockSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """``NoeudStock`` : chantier › magasin › familles."""

    id = serializers.CharField()
    libelle = serializers.CharField()
    type = serializers.CharField()
    nombreArticles = serializers.IntegerField(required=False)  # noqa: N815 — nom du web
    enfants = serializers.ListField(child=serializers.DictField())


# --- Mouvements ---------------------------------------------------------------------
class MouvementSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """``MouvementStockDto``. Contexte attendu : ``parametres``, un
    ``ParametresParChantier`` (délai de relance Q-F, dérive d'horloge
    RG-S11, lus une fois par chantier et par requête)."""

    article_id_article = serializers.UUIDField(source="article_id")
    magasin_id_magasin = serializers.UUIDField(source="magasin_id")
    logement_id_logement = serializers.UUIDField(source="logement_id", allow_null=True)
    type_mouvement_code_type_mouvement = serializers.CharField(source="type_mouvement_id")
    sens = serializers.IntegerField(source="type_mouvement.sens")
    statut_validation = serializers.SerializerMethodField()
    utilisateur_id_utilisateur = serializers.UUIDField(source="utilisateur_id")
    nom_auteur = serializers.CharField(source="utilisateur.nom_complet")
    code_unite = serializers.CharField(source="unite_mesure_id")
    corps_etat = serializers.CharField(source="corps_etat_id", allow_null=True)
    mouvement_annule_uuid = serializers.UUIDField(source="mouvement_annule_id", allow_null=True)
    derive_horloge = serializers.SerializerMethodField()

    class Meta:
        model = MouvementStock
        fields = [
            "uuid",
            "article_id_article",
            "magasin_id_magasin",
            "logement_id_logement",
            "type_mouvement_code_type_mouvement",
            "sens",
            "quantite_saisie",
            "quantite_base",
            "code_unite",
            "date_operation",
            "horodatage_appareil",
            "horodatage_serveur",
            "statut_validation",
            "reference_externe",
            "utilisateur_id_utilisateur",
            "nom_auteur",
            "motif",
            "corps_etat",
            "beneficiaire",
            "mouvement_annule_uuid",
            "derive_horloge",
        ]

    def get_statut_validation(self, obj: MouvementStock) -> str:
        parametres = self.context["parametres"]
        return selecteurs.statut_derive(
            obj, parametres.delai_relance_h(obj.magasin.chantier_id), parametres.maintenant
        )

    def get_derive_horloge(self, obj: MouvementStock) -> bool:
        """RG-S11 : dérive entre l'heure de l'appareil et celle du serveur
        au-delà de ``derive_horloge_max_min`` (signalée, jamais bloquante)."""
        limite = timedelta(
            minutes=self.context["parametres"].derive_max_min(obj.magasin.chantier_id)
        )
        return abs(obj.horodatage_serveur - obj.horodatage_appareil) > limite


class MouvementEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Corps de ``POST /mouvements`` (champs envoyés par le web et le mobile).
    ``uuid`` : identifiant généré par le client, pour l'idempotence."""

    uuid = serializers.UUIDField(required=False)
    magasin_id_magasin = serializers.UUIDField()
    article_id_article = serializers.PrimaryKeyRelatedField(
        queryset=selecteurs_referentiels.articles()
    )
    type_mouvement_code_type_mouvement = serializers.PrimaryKeyRelatedField(
        queryset=selecteurs_referentiels.types_mouvement()
    )
    quantite_saisie = _quantite(min_value=Decimal("0.001"))
    code_unite = serializers.CharField(max_length=32, required=False, allow_null=True)
    logement_id_logement = serializers.PrimaryKeyRelatedField(
        queryset=selecteurs_organisation.logements(), required=False, allow_null=True
    )
    corps_etat = serializers.PrimaryKeyRelatedField(
        queryset=selecteurs_referentiels.corps_etat(), required=False, allow_null=True
    )
    beneficiaire = serializers.CharField(
        max_length=120, required=False, allow_null=True, allow_blank=True
    )
    motif = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    reference_externe = serializers.CharField(
        max_length=120, required=False, allow_null=True, allow_blank=True
    )
    date_operation = serializers.DateTimeField(required=False)
    horodatage_appareil = serializers.DateTimeField(required=False)


class DecisionEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Décision sur un mouvement à valider (EF-STK-09). Motif obligatoire
    pour un refus (ET-2 « rejeté (motif) »)."""

    decision = serializers.ChoiceField(choices=list(DECISIONS))
    motif = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    uuid = serializers.UUIDField(required=False)


class AnnulationEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Contre-mouvement (RG-S8, EF-STK-11) : la justification est obligatoire."""

    motif = serializers.CharField()


# --- Alertes -----------------------------------------------------------------------
class AlerteSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    article_id_article = serializers.UUIDField(source="stock_courant.seuil_stock.article_id")
    magasin_id_magasin = serializers.UUIDField(source="stock_courant.seuil_stock.magasin_id")
    designation = serializers.CharField(source="stock_courant.seuil_stock.article.designation")

    class Meta:
        model = Alerte
        fields = [
            "id_alerte",
            "type_alerte",
            "niveau",
            "message",
            "date_emission",
            "statut",
            "article_id_article",
            "magasin_id_magasin",
            "designation",
        ]
