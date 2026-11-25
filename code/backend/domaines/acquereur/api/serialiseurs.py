"""Formes de l'espace acquéreur : ``features/acquereur/api/dto.ts`` du web
(décimaux en chaîne, statuts du MPD-5)."""

from rest_framework import serializers


class EtapeAcquereurSerializer(serializers.Serializer):  # type: ignore[type-arg]
    id_etape = serializers.UUIDField()
    libelle_etape = serializers.CharField()
    libelle_corps_etat = serializers.CharField()
    couleur_corps_etat = serializers.CharField()
    statut = serializers.CharField()
    date_franchissement = serializers.DateField(allow_null=True)


class AvancementLogementSerializer(serializers.Serializer):  # type: ignore[type-arg]
    numero_logement = serializers.CharField()
    libelle_zone = serializers.CharField()
    libelle_type_logement = serializers.CharField()
    pourcentage_valide = serializers.DecimalField(max_digits=14, decimal_places=3)
    pourcentage_declare = serializers.DecimalField(max_digits=14, decimal_places=3)
    date_livraison_prevue = serializers.DateField(allow_null=True)
    etapes = EtapeAcquereurSerializer(many=True)


class NotificationAcquereurSerializer(serializers.Serializer):  # type: ignore[type-arg]
    id_notification = serializers.UUIDField()
    libelle_etape = serializers.CharField()
    date_franchissement = serializers.DateTimeField()
    lue = serializers.BooleanField()
