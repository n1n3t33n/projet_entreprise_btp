"""Administration du domaine « organisation » : lecture seule (arbitrage Q5).

Chantier et magasin se consultent dans l'admin ; leur saisie passera par
l'API des référentiels (B2), qui valide et trace.
"""

from django.contrib import admin

from domaines.organisation.models import Chantier, Magasin
from socle.admin_outils import AdminLectureSeule


@admin.register(Chantier)
class AdminChantier(AdminLectureSeule):
    list_display = ("code", "nom", "statut", "date_debut")
    search_fields = ("code", "nom")


@admin.register(Magasin)
class AdminMagasin(AdminLectureSeule):
    list_display = ("code", "nom", "chantier", "actif")
    search_fields = ("code", "nom")
