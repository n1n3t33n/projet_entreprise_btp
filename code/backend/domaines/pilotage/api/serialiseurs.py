"""Formes du rapport hebdomadaire et des indicateurs d'usage : une liste de
lignes (rubrique, indicateur, valeur), la même que les colonnes du CSV."""

from rest_framework import serializers

JOURS_PAR_DEFAUT = 7
JOURS_MAXIMUM = 90


class LigneIndicateurSerializer(serializers.Serializer):  # type: ignore[type-arg]
    rubrique = serializers.CharField()
    indicateur = serializers.CharField()
    valeur = serializers.JSONField()


class RapportSerializer(serializers.Serializer):  # type: ignore[type-arg]
    semaine = serializers.CharField()
    du = serializers.DateField()
    au = serializers.DateField()
    lignes = LigneIndicateurSerializer(many=True)


class UsageSerializer(serializers.Serializer):  # type: ignore[type-arg]
    du = serializers.DateField()
    au = serializers.DateField()
    lignes = LigneIndicateurSerializer(many=True)


class FiltreUsageSerializer(serializers.Serializer):  # type: ignore[type-arg]
    jours = serializers.IntegerField(
        required=False, default=JOURS_PAR_DEFAUT, min_value=1, max_value=JOURS_MAXIMUM
    )
