"""Notifications 0005 — « étape franchie » pour l'acquéreur (EF-ACQ-02, Q-BB).

Une notification à chaque étape validée de son logement, adressée au seul
acquéreur de ce logement (RG-D10, restriction du rôle ACQUEREUR à son
logement dans identite/selecteurs/titulaires.py). Valeurs figées.
"""

from typing import Any

from django.db import migrations

CODE = "ETAPE_FRANCHIE"


def declarer(apps: Any, schema_editor: Any) -> None:
    TypeNotification = apps.get_model("notifications", "TypeNotification")
    AbonnementNotification = apps.get_model("notifications", "AbonnementNotification")
    TypeNotification.objects.update_or_create(
        code_type=CODE,
        defaults={
            "libelle": "Étape franchie",
            "modele_message": "Une nouvelle étape est franchie pour votre logement "
            "{logement} : {etape}.",
            "canal_defaut": "APPLICATION",
        },
    )
    AbonnementNotification.objects.get_or_create(
        type_notification_id=CODE, role_id="ACQUEREUR", defaults={"canal": "APPLICATION"}
    )


def retirer(apps: Any, schema_editor: Any) -> None:
    apps.get_model("notifications", "Notification").objects.filter(
        type_notification_id=CODE
    ).delete()
    apps.get_model("notifications", "AbonnementNotification").objects.filter(
        type_notification_id=CODE
    ).delete()
    apps.get_model("notifications", "TypeNotification").objects.filter(code_type=CODE).delete()


class Migration(migrations.Migration):
    dependencies = [("notifications", "0004_permissions")]

    operations = [migrations.RunPython(declarer, retirer)]
