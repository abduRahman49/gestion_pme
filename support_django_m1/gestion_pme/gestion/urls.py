from django.urls import path
from . import views

app_name = "gestion"
urlpatterns = [
    path("", views.tableau_bord, name="tableau_bord"),
    path("clients/", views.liste_clients, name="liste_clients"),
    path("clients/nouveau/", views.creer_client, name="creer_client"),
    path("clients/<int:pk>/", views.detail_client, name="detail_client"),
    path("clients/<int:pk>/modifier/", views.modifier_client, name="modifier_client"),
    path("clients/<int:pk>/supprimer/", views.supprimer_client, name="supprimer_client"),
    path("prestations/nouvelle/", views.creer_prestation, name="creer_prestation"),
    path("prestations/<int:pk>/modifier/", views.modifier_prestation, name="modifier_prestation"),
    path("prestations/<int:pk>/supprimer/", views.supprimer_prestation, name="supprimer_prestation"),
]
