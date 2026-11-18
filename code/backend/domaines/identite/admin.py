"""Administration Django du domaine identité (exigence 6.10, arbitrage Q5).

Accès : droit « technique / admin » de la matrice (``Utilisateur.is_staff``
et ``has_perm`` sont calculés), jamais un booléen stocké.

Périmètre :
  * modifiables : ``role`` et ``permission`` (référentiels à clé simple) ;
  * lecture seule : ``utilisateur`` et ``appareil`` — créer un compte ou
    révoquer un appareil passe par l'API, qui valide et trace (RG-D9) ;
  * NON enregistrés : ``droit_accorde``, ``affectation_role``,
    ``membre_equipe`` (clés composites, que l'admin de Django 5.2 ne sait pas
    afficher) et ``journal_audit`` (clé composite et immuable).
"""

from django.contrib import admin

from domaines.identite.models import Appareil, Permission, Role, Utilisateur
from socle.admin_outils import AdminLectureSeule


@admin.register(Role)
class AdminRole(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("code_role", "libelle", "systeme", "actif")
    search_fields = ("code_role", "libelle")


@admin.register(Permission)
class AdminPermission(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("code_permission", "module", "ressource", "action", "libelle")
    list_filter = ("module", "action")
    search_fields = ("code_permission", "libelle")


@admin.register(Utilisateur)
class AdminUtilisateur(AdminLectureSeule):
    list_display = ("identifiant", "nom", "prenom", "fonction", "statut", "date_creation")
    list_filter = ("statut",)
    search_fields = ("identifiant", "nom", "prenom")
    # L'empreinte du mot de passe n'est jamais affichée.
    exclude = ("password",)


@admin.register(Appareil)
class AdminAppareil(AdminLectureSeule):
    list_display = (
        "utilisateur",
        "plateforme",
        "version_application",
        "statut",
        "derniere_synchronisation",
    )
    list_filter = ("statut", "plateforme")
