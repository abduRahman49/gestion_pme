from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("comptes/connexion/", auth_views.LoginView.as_view(), name="login"),
    path("comptes/deconnexion/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("gestion.urls")),
]
