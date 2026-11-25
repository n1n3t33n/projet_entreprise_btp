"""Administration du domaine « organisation » (arbitrage Q5).

Chantier et magasin se consultent en lecture seule : leur saisie passe par
l'API des référentiels, qui valide les données. Les référentiels à clé simple
(type de logement, paramètres de chantier) se modifient ici.
"""

from django.contrib import admin

from domaines.organisation.models import (
    Acquereur,
    Chantier,
    Magasin,
    ParametreChantier,
    TypeLogement,
)
from socle.admin_outils import AdminLectureSeule


@admin.register(TypeLogement)
class AdminTypeLogement(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("code_type", "libelle", "surface_reference", "actif")
    search_fields = ("code_type", "libelle")


@admin.register(ParametreChantier)
class AdminParametreChantier(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("chantier", "cle", "valeur", "type_valeur", "libelle")
    list_filter = ("chantier", "type_valeur")
    search_fields = ("cle", "libelle")


@admin.register(Chantier)
class AdminChantier(AdminLectureSeule):
    list_display = ("code", "nom", "statut", "date_debut")
    search_fields = ("code", "nom")


@admin.register(Magasin)
class AdminMagasin(AdminLectureSeule):
    list_display = ("code", "nom", "chantier", "actif")
    search_fields = ("code", "nom")


@admin.register(Acquereur)
class AdminAcquereur(admin.ModelAdmin):  # type: ignore[type-arg]
    """Acquéreurs des logements (MPD-2) ; le compte se rattache par l'API des
    comptes (acquereur_id_acquereur)."""

    list_display = ("nom", "prenom", "logement", "date_acquisition")
    search_fields = ("nom", "prenom", "logement__numero")
