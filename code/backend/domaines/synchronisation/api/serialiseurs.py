"""Formes d'entrée et de sortie de la synchronisation (SQ-2, EF-SYN-02).

Un lot : ``id_lot`` (créé par le téléphone), ``horodatage_envoi`` (heure de
l'appareil, contrôle de dérive RG-S11) et la liste ordonnée des événements.
Chaque événement : ``uuid``, ``type`` (voir ``socle/synchronisation.py``),
``horodatage_appareil`` (heure de saisie) et ``charge_utile`` — le corps de la
route REST correspondante (Q-AE).

Réponse : un résultat par événement ; le téléphone rapproche chaque résultat
par ``uuid_evenement`` (ET-3), l'ordre de la liste n'est pas garanti.
"""

from rest_framework import serializers

from domaines.synchronisation.constantes import EVENEMENTS_PAR_LOT_MAX
from domaines.synchronisation.models import LotSynchronisation, ResultatEvenement


class EvenementEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    uuid = serializers.UUIDField()
    type = serializers.CharField(max_length=64)
    horodatage_appareil = serializers.DateTimeField(required=False, allow_null=True)
    charge_utile = serializers.DictField()


class LotEntreeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    id_lot = serializers.UUIDField()
    horodatage_envoi = serializers.DateTimeField(required=False, allow_null=True)
    evenements = serializers.ListField(
        child=EvenementEntreeSerializer(), min_length=1, max_length=EVENEMENTS_PAR_LOT_MAX
    )


class ResultatSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    class Meta:
        model = ResultatEvenement
        fields = ["uuid_evenement", "statut", "code_rejet", "motif_rejet"]


class LotSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    resultats = ResultatSerializer(many=True, read_only=True)

    class Meta:
        model = LotSynchronisation
        fields = [
            "id_lot",
            "date_reception",
            "nombre_evenements",
            "nombre_acceptes",
            "nombre_rejetes",
            "duree_ms",
            "resultats",
        ]
