"""Notifications 0002 — catalogue initial des types et abonnements (données).

Types de notification et rôles abonnés arbitrés le 2026-11-23 (Q-AP, Q-AQ).
Valeurs FIGÉES ici, comme toute migration : elles se règlent ensuite dans
l'administration (Q5). Un abonnement sans rôle désigne « la personne
concernée » par l'événement (cardinalité (0,1) de « abonne » au MCD).
"""

from typing import Any

from django.db import migrations

CATALOGUE: tuple[tuple[str, str, str], ...] = (
    (
        "SORTIE_A_VALIDER",
        "Sortie à valider",
        "Sortie de {quantite} {unite} de {article} au magasin {magasin}, saisie par "
        "{auteur} : votre décision est attendue.",
    ),
    ("VALIDATION_EN_RETARD", "Validation en retard", "{message}"),
    (
        "SORTIE_REFUSEE",
        "Sortie refusée",
        "Votre sortie de {quantite} {unite} de {article} a été refusée : {motif}",
    ),
    ("SEUIL_MINIMAL", "Stock sous le seuil minimal", "{message}"),
    ("SEUIL_CRITIQUE", "Stock sous le seuil critique", "{message}"),
    ("STOCK_NEGATIF", "Stock négatif", "{message}"),
    (
        "ETAPE_A_CONTROLER",
        "Étape à contrôler",
        "{etape} du logement {logement}, déclarée terminée par {auteur} : contrôle attendu.",
    ),
    (
        "ETAPE_REJETEE",
        "Étape rejetée",
        "{etape} du logement {logement} a été rejetée au contrôle : {motif}",
    ),
    ("ETAPE_BLOQUEE", "Étape bloquée", "{etape} du logement {logement} est bloquée : {motif}"),
    (
        "MANQUE_MATERIEL",
        "Manque de matériel",
        "{etape} du logement {logement} est bloquée faute de {article}.",
    ),
    (
        "ETAPE_EN_RETARD",
        "Étape en retard",
        "{etape} du logement {logement} est en retard (prévue le {date_prevue}).",
    ),
    ("ANOMALIE_SYNCHRONISATION", "Anomalie de synchronisation", "{description}"),
    (
        "RAPPORT_HEBDOMADAIRE",
        "Rapport hebdomadaire",
        "Le rapport de la semaine {semaine} est disponible.",
    ),
)


ABONNEMENTS: tuple[tuple[str, str | None], ...] = (
    ("SORTIE_A_VALIDER", "GESTIONNAIRE_STOCK"),
    ("VALIDATION_EN_RETARD", "GESTIONNAIRE_STOCK"),
    ("SORTIE_REFUSEE", None),
    ("SEUIL_MINIMAL", "GESTIONNAIRE_STOCK"),
    ("SEUIL_MINIMAL", "MAGASINIER"),
    ("SEUIL_CRITIQUE", "GESTIONNAIRE_STOCK"),
    ("SEUIL_CRITIQUE", "MAGASINIER"),
    ("STOCK_NEGATIF", "GESTIONNAIRE_STOCK"),
    ("ETAPE_A_CONTROLER", "CHEF_CHANTIER"),
    ("ETAPE_A_CONTROLER", "RESPONSABLE_TECHNIQUE"),
    ("ETAPE_REJETEE", None),
    ("ETAPE_BLOQUEE", "CHEF_CHANTIER"),
    ("ETAPE_BLOQUEE", "RESPONSABLE_TECHNIQUE"),
    ("MANQUE_MATERIEL", "GESTIONNAIRE_STOCK"),
    ("ETAPE_EN_RETARD", "CHEF_CHANTIER"),
    ("ETAPE_EN_RETARD", "RESPONSABLE_TECHNIQUE"),
    ("ANOMALIE_SYNCHRONISATION", "GESTIONNAIRE_STOCK"),
    ("ANOMALIE_SYNCHRONISATION", "CHEF_CHANTIER"),
    ("RAPPORT_HEBDOMADAIRE", "DIRECTION"),
    ("RAPPORT_HEBDOMADAIRE", "RESPONSABLE_TECHNIQUE"),
)


def declarer(apps: Any, schema_editor: Any) -> None:
    TypeNotification = apps.get_model("notifications", "TypeNotification")
    AbonnementNotification = apps.get_model("notifications", "AbonnementNotification")
    for code, libelle, modele in CATALOGUE:
        TypeNotification.objects.update_or_create(
            code_type=code,
            defaults={"libelle": libelle, "modele_message": modele, "canal_defaut": "APPLICATION"},
        )
    for code, role in ABONNEMENTS:
        AbonnementNotification.objects.get_or_create(
            type_notification_id=code, role_id=role, defaults={"canal": "APPLICATION"}
        )


def retirer(apps: Any, schema_editor: Any) -> None:
    codes = [code for code, _libelle, _modele in CATALOGUE]
    apps.get_model("notifications", "AbonnementNotification").objects.filter(
        type_notification_id__in=codes
    ).delete()
    apps.get_model("notifications", "TypeNotification").objects.filter(code_type__in=codes).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0001_initial"),
        ("identite", "0004_referentiel_droits"),
    ]

    operations = [migrations.RunPython(declarer, retirer)]
