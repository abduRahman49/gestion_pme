from django.contrib import admin
from .models import Client, Prestation


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["nom", "email", "telephone"]
    search_fields = ["nom"]


@admin.register(Prestation)
class PrestationAdmin(admin.ModelAdmin):
    list_display = ["libelle", "client", "date", "montant", "statut"]
    list_filter = ["statut"]
    search_fields = ["libelle", "client__nom"]
