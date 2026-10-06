from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from .forms import ClientForm, PrestationForm
from .models import Client, Prestation


@login_required
def tableau_bord(request):
    total = Prestation.objects.filter(statut="TERMINEE").aggregate(
        total=Sum("montant", default=0)
    )["total"]
    return render(request, "gestion/tableau_bord.html", {
        "nombre_clients": Client.objects.count(),
        "nombre_prevues": Prestation.objects.filter(statut="PREVUE").count(),
        "total": total,
    })


@login_required
def liste_clients(request):
    q = request.GET.get("q", "").strip()
    clients = Client.objects.filter(nom__icontains=q)
    page = Paginator(clients, 5).get_page(request.GET.get("page"))
    return render(request, "gestion/liste_clients.html", {"page": page, "q": q})


@login_required
def detail_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, "gestion/detail_client.html", {"client": client})


@login_required
@permission_required("gestion.add_client", raise_exception=True)
@require_http_methods(["GET", "POST"])
def creer_client(request):
    form = ClientForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        client = form.save()
        messages.success(request, "Client créé.")
        return redirect("gestion:detail_client", pk=client.pk)
    return render(request, "gestion/formulaire.html", {
        "form": form, "titre": "Nouveau client",
    })


@login_required
@permission_required("gestion.change_client", raise_exception=True)
@require_http_methods(["GET", "POST"])
def modifier_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    form = ClientForm(
        request.POST if request.method == "POST" else None, instance=client
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Client modifié.")
        return redirect("gestion:detail_client", pk=client.pk)
    return render(request, "gestion/formulaire.html", {
        "form": form, "titre": "Modifier le client",
    })


@login_required
@permission_required("gestion.delete_client", raise_exception=True)
@require_http_methods(["GET", "POST"])
def supprimer_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        try:
            client.delete()
        except ProtectedError:
            messages.error(request, "Ce client possède des prestations : suppression impossible.")
            return redirect("gestion:detail_client", pk=pk)
        messages.success(request, "Client supprimé.")
        return redirect("gestion:liste_clients")
    return render(request, "gestion/confirmer_suppression.html", {"objet": client})


@login_required
@permission_required("gestion.add_prestation", raise_exception=True)
@require_http_methods(["GET", "POST"])
def creer_prestation(request):
    form = PrestationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        prestation = form.save()
        messages.success(request, "Prestation créée.")
        return redirect("gestion:detail_client", pk=prestation.client_id)
    return render(request, "gestion/formulaire.html", {
        "form": form, "titre": "Nouvelle prestation",
    })


@login_required
@permission_required("gestion.change_prestation", raise_exception=True)
@require_http_methods(["GET", "POST"])
def modifier_prestation(request, pk):
    prestation = get_object_or_404(Prestation, pk=pk)
    form = PrestationForm(
        request.POST if request.method == "POST" else None, instance=prestation
    )
    if request.method == "POST" and form.is_valid():
        prestation = form.save()
        messages.success(request, "Prestation modifiée.")
        return redirect("gestion:detail_client", pk=prestation.client_id)
    return render(request, "gestion/formulaire.html", {
        "form": form, "titre": "Modifier la prestation",
    })


@login_required
@permission_required("gestion.delete_prestation", raise_exception=True)
@require_http_methods(["GET", "POST"])
def supprimer_prestation(request, pk):
    prestation = get_object_or_404(Prestation, pk=pk)
    if request.method == "POST":
        client_id = prestation.client_id
        prestation.delete()
        messages.success(request, "Prestation supprimée.")
        return redirect("gestion:detail_client", pk=client_id)
    return render(request, "gestion/confirmer_suppression.html", {"objet": prestation})
