"""Routes racines (version provisoire, complétée avec l'API identité)."""

from django.contrib import admin
from django.urls import path

from socle import sante

urlpatterns = [
    path("api/sante/vivacite", sante.vivacite, name="sante-vivacite"),
    path("api/sante/aptitude", sante.aptitude, name="sante-aptitude"),
    path("admin/", admin.site.urls),
]
