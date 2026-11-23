"""Sérialiseurs du domaine « référentiels » : ils fixent le CONTRAT d'API.

Formes reprises des DTO du web : ``features/referentiels/api/dto.ts``,
``features/gammes/api/dto.ts``, ``features/parametrage/api/dto.ts`` et, pour
les listes de l'écran Stock, ``features/stock/api/dto.ts`` et
``features/avancement/api/dto.ts``. Décimaux transportés en chaîne.
"""

from decimal import Decimal
from typing import Any, cast

from rest_framework import serializers

from domaines.referentiels import selecteurs
from domaines.referentiels.constantes import (
    OPERATEURS_REGLE,
    ORIGINES_ARTICLE,
    TYPES_EVENEMENT_REGLE,
)
from domaines.referentiels.models import (
    Article,
    CategorieArticle,
    CorpsEtat,
    EtapeModele,
    Gamme,
    MotifBlocage,
    RegleValidation,
    TypeMouvement,
    UniteMesure,
)
from socle import importation


class CategorieSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """``CategorieDto``. ``code_parent`` toujours null : familles plates comme
    au MPD (arbitrage Q-E) ; ajout compatible pour l'écran Stock (F-11)."""

    code_parent = serializers.SerializerMethodField()

    class Meta:
        model = CategorieArticle
        fields = ["code_categorie", "libelle", "code_parent"]

    def get_code_parent(self, obj: CategorieArticle) -> str | None:
        return None


class UniteSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    class Meta:
        model = UniteMesure
        fields = ["code_unite", "libelle", "type_unite"]


class ArticleSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """``ArticleDto`` de l'écran Référentiels (EF-REF-03)."""

    origine = serializers.ChoiceField(choices=list(ORIGINES_ARTICLE))
    code_barre = serializers.CharField(
        max_length=32, allow_null=True, allow_blank=True, required=False
    )
    categorie_article_code_categorie = serializers.PrimaryKeyRelatedField(
        source="categorie_article",
        queryset=selecteurs.categories(),
        allow_null=True,
        required=False,
    )
    unite_mesure_code_unite = serializers.PrimaryKeyRelatedField(
        source="unite_mesure", queryset=selecteurs.unites()
    )

    class Meta:
        model = Article
        fields = [
            "id_article",
            "code",
            "designation",
            "origine",
            "code_barre",
            "actif",
            "categorie_article_code_categorie",
            "unite_mesure_code_unite",
        ]
        read_only_fields = ["id_article"]

    def validate_code_barre(self, valeur: str | None) -> str | None:
        # Une chaîne vide n'est pas un code-barres : elle violerait l'unicité.
        return valeur or None


class CorpsEtatSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """``CorpsEtatDto`` (EF-REF-05)."""

    class Meta:
        model = CorpsEtat
        fields = ["code_corps_etat", "libelle", "ordre", "couleur"]


class GammeSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """``GammeDto`` : la gamme, le libellé de son type de logement, son nombre
    d'étapes et son poids total (calculés par ``selecteurs.gammes``)."""

    type_logement_code_type = serializers.CharField(source="type_logement_id", read_only=True)
    libelle_type_logement = serializers.CharField(source="type_logement.libelle", read_only=True)
    nombre_etapes = serializers.IntegerField(read_only=True, default=0)
    poids_total = serializers.DecimalField(
        max_digits=14, decimal_places=3, read_only=True, default=Decimal("0")
    )

    class Meta:
        model = Gamme
        fields = [
            "id_gamme",
            "version",
            "libelle",
            "statut",
            "date_activation",
            "type_logement_code_type",
            "libelle_type_logement",
            "nombre_etapes",
            "poids_total",
        ]
        read_only_fields = fields


class EtapeModeleSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """``EtapeModeleDto`` (lecture)."""

    corps_etat_code_corps_etat = serializers.CharField(source="corps_etat_id")
    libelle_corps_etat = serializers.CharField(source="corps_etat.libelle")
    couleur_corps_etat = serializers.CharField(source="corps_etat.couleur")
    gamme_id_gamme = serializers.UUIDField(source="gamme_id")

    class Meta:
        model = EtapeModele
        fields = [
            "id_etape_modele",
            "code",
            "libelle",
            "ordre",
            "poids",
            "controle_requis",
            "corps_etat_code_corps_etat",
            "libelle_corps_etat",
            "couleur_corps_etat",
            "gamme_id_gamme",
        ]


class EtapeModeleEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """``EtapeModeleCorps`` : une étape envoyée par l'écran Gammes. Le poids
    arrive en nombre ; il est rangé en numeric(14,3)."""

    id_etape_modele = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField(max_length=32)
    libelle = serializers.CharField(max_length=120)
    ordre = serializers.IntegerField(min_value=1)
    poids = serializers.DecimalField(max_digits=14, decimal_places=3, min_value=0)
    controle_requis = serializers.BooleanField()
    corps_etat_code_corps_etat = serializers.PrimaryKeyRelatedField(
        queryset=selecteurs.corps_etat()
    )

    def validate_corps_etat_code_corps_etat(self, valeur: CorpsEtat) -> str:
        return str(valeur.pk)


class EtapesEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    etapes = EtapeModeleEntreeSerializer(many=True)


class TypeMouvementSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    class Meta:
        model = TypeMouvement
        fields = [
            "code_type_mouvement",
            "libelle",
            "sens",
            "motif_obligatoire",
            "destination_obligatoire",
        ]


class MotifBlocageSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    class Meta:
        model = MotifBlocage
        fields = ["code_motif", "libelle", "requiert_article", "actif"]


class RegleSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """``RegleValidationDto`` (EF-REF-08). ``type_evenement`` et ``operateur``
    sont contrôlés ici, le MPD ne les contraignant pas en base."""

    type_evenement = serializers.ChoiceField(choices=list(TYPES_EVENEMENT_REGLE))
    operateur = serializers.ChoiceField(choices=list(OPERATEURS_REGLE))
    valeur_seuil = serializers.DecimalField(
        max_digits=14, decimal_places=3, allow_null=True, required=False
    )
    delai_heures = serializers.IntegerField(allow_null=True, required=False, min_value=1)

    class Meta:
        model = RegleValidation
        fields = [
            "id_regle",
            "type_evenement",
            "champ_teste",
            "operateur",
            "valeur_seuil",
            "delai_heures",
        ]
        read_only_fields = ["id_regle"]


# --- Import CSV (EF-ADM-02) : formes de ``features/admin/api/import-csv-dto.ts``
class ImportEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Corps des deux appels : la cible et le texte brut du fichier. Les
    cibles possibles sont celles que les domaines ont déclarées."""

    cible = serializers.ChoiceField(choices=[])
    contenu = serializers.CharField(trim_whitespace=False)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Choix lus à chaque instance, jamais au chargement du module : les
        # domaines déclarent leurs cibles au démarrage, dans un ordre
        # quelconque (ce module peut être chargé avant certains d'entre eux).
        champ = cast(serializers.ChoiceField, self.fields["cible"])
        champ.choices = sorted(importation.CIBLES)


class LigneImportSerializer(serializers.Serializer):  # type: ignore[type-arg]
    numero = serializers.IntegerField()
    valeurs = serializers.ListField(child=serializers.CharField())
    erreur = serializers.CharField(allow_null=True)


class RapportImportSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """``RapportImportDto`` : ``colonnes`` dit au web quelles colonnes le
    serveur attend (I-37)."""

    cible = serializers.CharField()
    colonnes = serializers.ListField(child=serializers.CharField())
    lignes = LigneImportSerializer(many=True)
    nombre_valides = serializers.IntegerField()
    nombre_erreurs = serializers.IntegerField()


class ResultatImportSerializer(serializers.Serializer):  # type: ignore[type-arg]
    cible = serializers.CharField()
    nombre_importees = serializers.IntegerField()
