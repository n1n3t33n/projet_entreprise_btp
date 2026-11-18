"""Administration des référentiels à clé simple du MPD-3 (arbitrage Q5).

Modifiables ici : familles, unités, corps d'état, types de mouvement, motifs
de blocage, règles de validation. Les articles et les gammes passent par
l'API (règles de publication, import CSV). ``conditionnement`` n'est pas
enregistré : clé primaire composite, que l'admin de Django 5.2 ne sait pas
afficher (I-15).
"""

from django.contrib import admin

from domaines.referentiels.models import (
    CategorieArticle,
    CorpsEtat,
    MotifBlocage,
    RegleValidation,
    TypeMouvement,
    UniteMesure,
)


@admin.register(CategorieArticle)
class AdminCategorieArticle(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("code_categorie", "libelle")
    search_fields = ("code_categorie", "libelle")


@admin.register(UniteMesure)
class AdminUniteMesure(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("code_unite", "libelle", "type_unite")
    list_filter = ("type_unite",)


@admin.register(CorpsEtat)
class AdminCorpsEtat(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("code_corps_etat", "libelle", "ordre", "couleur")
    ordering = ("ordre",)


@admin.register(TypeMouvement)
class AdminTypeMouvement(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        "code_type_mouvement",
        "libelle",
        "sens",
        "motif_obligatoire",
        "destination_obligatoire",
    )


@admin.register(MotifBlocage)
class AdminMotifBlocage(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("code_motif", "libelle", "requiert_article", "actif")


@admin.register(RegleValidation)
class AdminRegleValidation(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("type_evenement", "champ_teste", "operateur", "valeur_seuil", "delai_heures")
    list_filter = ("type_evenement",)
