"""Référentiels 0004 — types de mouvement employés par le serveur (données).

``type_mouvement`` est un référentiel vivant (MPD-3) ; ces cinq lignes sont
créées ici parce que le domaine stock les utilise lui-même et ne doit pas
dépendre du jeu de démonstration :
  * ENT_STOCK_INITIAL — stock de départ importé (EF-ADM-02) ;
  * AJU_INVENTAIRE_PLUS / AJU_INVENTAIRE_MOINS — ajustement d'inventaire
    (RG-S3, RG-S9). Deux codes plutôt qu'un type signé : ``sens`` vaut +1 ou
    −1 au MPD (arbitrage Q-Q ; le mobile n'a qu'``AJU_INVENTAIRE``, I-21) ;
  * ANN_PLUS / ANN_MOINS — contre-mouvement qui corrige une sortie ou une
    entrée (RG-S8, EF-STK-11).
Motif obligatoire pour les ajustements et les annulations (RG-S3, RG-S8).
Valeurs recopiées (une migration reste figée) depuis domaines/stock/constantes.py.
"""

from typing import Any

from django.db import migrations

TYPES = [
    # (code, libellé, sens, motif obligatoire)
    ("ENT_STOCK_INITIAL", "Stock de départ", 1, False),
    ("AJU_INVENTAIRE_PLUS", "Ajustement d'inventaire (excédent)", 1, True),
    ("AJU_INVENTAIRE_MOINS", "Ajustement d'inventaire (manquant)", -1, True),
    ("ANN_PLUS", "Annulation d'une sortie", 1, True),
    ("ANN_MOINS", "Annulation d'une entrée", -1, True),
]


def creer(apps: Any, schema_editor: Any) -> None:
    TypeMouvement = apps.get_model("referentiels", "TypeMouvement")
    for code, libelle, sens, motif in TYPES:
        TypeMouvement.objects.update_or_create(
            code_type_mouvement=code,
            defaults={
                "libelle": libelle,
                "sens": sens,
                "motif_obligatoire": motif,
                "destination_obligatoire": False,
            },
        )


def retirer(apps: Any, schema_editor: Any) -> None:
    TypeMouvement = apps.get_model("referentiels", "TypeMouvement")
    TypeMouvement.objects.filter(code_type_mouvement__in=[t[0] for t in TYPES]).delete()


class Migration(migrations.Migration):
    dependencies = [("referentiels", "0003_permissions")]

    operations = [migrations.RunPython(creer, retirer)]
