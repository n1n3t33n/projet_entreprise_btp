"""Administration des notifications (arbitrage Q5) : types et abonnements
se règlent ici ; les notifications émises ne s'y modifient pas."""

from django.contrib import admin

from domaines.notifications.models import AbonnementNotification, TypeNotification


@admin.register(TypeNotification)
class AdminTypeNotification(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("code_type", "libelle", "canal_defaut")
    search_fields = ("code_type", "libelle")


@admin.register(AbonnementNotification)
class AdminAbonnementNotification(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("type_notification", "role", "canal", "actif")
    list_filter = ("type_notification", "role", "actif")
