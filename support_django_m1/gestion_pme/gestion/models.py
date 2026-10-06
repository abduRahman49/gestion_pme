from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Client(models.Model):
    nom = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["nom", "pk"]

    def __str__(self):
        return self.nom


class Prestation(models.Model):
    STATUTS = [
        ("PREVUE", "Prévue"),
        ("TERMINEE", "Terminée"),
        ("ANNULEE", "Annulée"),
    ]
    client = models.ForeignKey(
        Client, on_delete=models.PROTECT, related_name="prestations"
    )
    libelle = models.CharField("libellé", max_length=150)
    date = models.DateField(default=timezone.localdate)
    montant = models.DecimalField(
        "montant en FCFA", max_digits=10, decimal_places=0,
        validators=[MinValueValidator(0)],
    )
    statut = models.CharField(max_length=8, choices=STATUTS, default="PREVUE")

    class Meta:
        ordering = ["-date", "-pk"]

    def __str__(self):
        return self.libelle
