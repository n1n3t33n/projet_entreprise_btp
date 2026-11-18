"""Sérialiseurs du domaine « organisation » : ils fixent le CONTRAT d'API.

Chaque forme reprend le DTO que l'écran consomme déjà (rapport B0 § 3.4) :
``features/referentiels/api/dto.ts`` pour les écrans Référentiels,
``features/stock/api/dto.ts`` pour les listes utilisées par l'écran Stock,
``features/parametrage/api/dto.ts`` pour le Paramétrage. Quand deux écrans
attendent deux formes pour la même table (le magasin, I-30), chaque route rend
la forme de son écran.
"""

from rest_framework import serializers

from domaines.organisation import selecteurs
from domaines.organisation.constantes import (
    STATUTS_CHANTIER,
    STATUTS_LOGEMENT,
    TYPES_VALEUR,
    TYPES_ZONE,
)
from domaines.organisation.models import (
    Chantier,
    Logement,
    Magasin,
    ParametreChantier,
    TypeLogement,
    Zone,
)


class ChantierSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """``ChantierDto`` (web, Référentiels)."""

    statut = serializers.ChoiceField(choices=list(STATUTS_CHANTIER))

    class Meta:
        model = Chantier
        fields = ["id_chantier", "code", "nom", "programme", "date_debut", "statut"]
        read_only_fields = ["id_chantier"]


class MagasinReferentielSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """``MagasinDto`` de l'écran Référentiels : ``nom``, ``chantier_id_chantier``."""

    chantier_id_chantier = serializers.PrimaryKeyRelatedField(
        source="chantier", queryset=selecteurs.chantiers()
    )
    libelle_chantier = serializers.CharField(source="chantier.nom", read_only=True)

    class Meta:
        model = Magasin
        fields = ["id_magasin", "code", "nom", "actif", "chantier_id_chantier", "libelle_chantier"]
        read_only_fields = ["id_magasin"]


class MagasinStockSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """``MagasinDto`` de l'écran Stock : ``libelle`` et ``id_chantier`` (I-30)."""

    libelle = serializers.CharField(source="nom")
    id_chantier = serializers.UUIDField(source="chantier_id")
    libelle_chantier = serializers.CharField(source="chantier.nom")

    class Meta:
        model = Magasin
        fields = ["id_magasin", "code", "libelle", "id_chantier", "libelle_chantier"]


class ZoneSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    type_zone = serializers.ChoiceField(choices=list(TYPES_ZONE))
    chantier_id_chantier = serializers.PrimaryKeyRelatedField(
        source="chantier", queryset=selecteurs.chantiers()
    )

    class Meta:
        model = Zone
        fields = ["id_zone", "code", "nom", "type_zone", "chantier_id_chantier"]
        read_only_fields = ["id_zone"]


class TypeLogementSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    class Meta:
        model = TypeLogement
        fields = ["code_type", "libelle", "surface_reference", "actif"]


class LogementSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """``LogementDto``. Statut = cycle de vie {A_VENIR, EN_COURS, LIVRE}
    (arbitrage Q-A ; le module Référentiels du web s'alignera, F-11)."""

    statut = serializers.ChoiceField(choices=list(STATUTS_LOGEMENT))
    zone_id_zone = serializers.PrimaryKeyRelatedField(source="zone", queryset=selecteurs.zones())
    type_logement_code_type = serializers.PrimaryKeyRelatedField(
        source="type_logement", queryset=selecteurs.types_logement()
    )

    class Meta:
        model = Logement
        fields = [
            "id_logement",
            "numero",
            "statut",
            "date_livraison_prevue",
            "zone_id_zone",
            "type_logement_code_type",
        ]
        read_only_fields = ["id_logement"]


class ZoneArborescenceSerializer(serializers.Serializer):  # type: ignore[type-arg]
    zone = ZoneSerializer(source="*")
    logements = LogementSerializer(many=True)


class ArborescenceSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """``ChantierArbreDto`` : le chantier, ses zones et leurs logements."""

    chantier = ChantierSerializer(source="*")
    zones = ZoneArborescenceSerializer(many=True)


class LogementDestinationSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """``LogementDestinationDto`` (écran Stock, sortie vers un logement)."""

    libelle_zone = serializers.CharField(source="zone.nom")
    libelle_type = serializers.CharField(source="type_logement.libelle")

    class Meta:
        model = Logement
        fields = ["id_logement", "numero", "libelle_zone", "libelle_type"]


class ParametreSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """``ParametreChantierDto`` (EF-REF-07). ``chantier_id_chantier`` est un
    ajout compatible : facultatif en entrée tant qu'il n'y a qu'un chantier
    (I-35)."""

    type_valeur = serializers.ChoiceField(choices=list(TYPES_VALEUR))
    libelle = serializers.CharField(
        max_length=120, allow_null=True, required=False, allow_blank=True
    )
    chantier_id_chantier = serializers.UUIDField(source="chantier_id", required=False)

    class Meta:
        model = ParametreChantier
        fields = ["id_parametre", "cle", "valeur", "type_valeur", "libelle", "chantier_id_chantier"]
        read_only_fields = ["id_parametre"]
