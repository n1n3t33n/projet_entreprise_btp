"""Formes de l'API des notifications (CL-5 ``Notification``, type web
``features/avancement/types/domaine.ts``), enrichies du type et de l'objet
en cause pour que l'écran puisse ouvrir celui-ci (écart Q-AN)."""

from rest_framework import serializers

from domaines.notifications.models import Notification

LIMITE_PAR_DEFAUT = 50
LIMITE_MAXIMALE = 200


class NotificationSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    code_type = serializers.CharField(source="type_notification_id")
    libelle_type = serializers.CharField(source="type_notification.libelle")
    est_lue = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id_notification",
            "code_type",
            "libelle_type",
            "message",
            "canal",
            "date_creation",
            "date_lecture",
            "est_lue",
            "id_objet",
        ]

    def get_est_lue(self, obj: Notification) -> bool:
        return obj.date_lecture is not None


class FiltreNotificationsSerializer(serializers.Serializer):  # type: ignore[type-arg]
    non_lues = serializers.BooleanField(required=False, default=False)
    limite = serializers.IntegerField(
        required=False, default=LIMITE_PAR_DEFAUT, min_value=1, max_value=LIMITE_MAXIMALE
    )


class CompteurSerializer(serializers.Serializer):  # type: ignore[type-arg]
    non_lues = serializers.IntegerField()


class LectureGroupeeSerializer(serializers.Serializer):  # type: ignore[type-arg]
    nombre = serializers.IntegerField()
