from django import forms
from .models import Client, Prestation


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["nom", "email", "telephone"]


class PrestationForm(forms.ModelForm):
    class Meta:
        model = Prestation
        fields = ["client", "libelle", "date", "montant", "statut"]
        widgets = {
            "date": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date"}
            )
        }
