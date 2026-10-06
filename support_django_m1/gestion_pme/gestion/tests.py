from decimal import Decimal
from django.contrib.auth.models import Permission, User
from django.test import Client as Navigateur, TestCase
from django.urls import reverse
from .forms import PrestationForm
from .models import Client, Prestation


class ParcoursGestionTests(TestCase):
    def setUp(self):
        self.lecteur = User.objects.create_user(username="lecteur")
        self.gestionnaire = User.objects.create_user(username="gestionnaire")
        self.gestionnaire.user_permissions.set(
            Permission.objects.filter(content_type__app_label="gestion")
        )
        self.entreprise = Client.objects.create(nom="Teranga Conseil")

    def test_visiteur_redirige_vers_connexion(self):
        url = reverse("gestion:liste_clients")
        self.assertRedirects(self.client.get(url), reverse("login") + "?next=" + url)

    def test_lecteur_ne_peut_pas_creer_meme_par_post_direct(self):
        self.client.force_login(self.lecteur)
        response = self.client.post(reverse("gestion:creer_client"), {"nom": "Intrus"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Client.objects.filter(nom="Intrus").exists())

    def test_creation_invalide_puis_creation_valide(self):
        self.client.force_login(self.gestionnaire)
        url = reverse("gestion:creer_client")
        response = self.client.post(url, {"nom": "", "email": "incorrect"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Client.objects.count(), 1)
        response = self.client.post(url, {"nom": "Baobab Services"})
        nouveau = Client.objects.get(nom="Baobab Services")
        self.assertRedirects(response, reverse("gestion:detail_client", args=[nouveau.pk]))

    def test_modification_ne_cree_pas_de_doublon(self):
        self.client.force_login(self.gestionnaire)
        self.client.post(reverse("gestion:modifier_client", args=[self.entreprise.pk]),
                         {"nom": "Teranga Formation"})
        self.entreprise.refresh_from_db()
        self.assertEqual(self.entreprise.nom, "Teranga Formation")
        self.assertEqual(Client.objects.count(), 1)

    def test_suppression_get_sans_effet_puis_post(self):
        self.client.force_login(self.gestionnaire)
        url = reverse("gestion:supprimer_client", args=[self.entreprise.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Client.objects.filter(pk=self.entreprise.pk).exists())
        self.client.post(url)
        self.assertFalse(Client.objects.filter(pk=self.entreprise.pk).exists())

    def test_client_lie_protege(self):
        Prestation.objects.create(client=self.entreprise, libelle="Audit", montant=25000)
        self.client.force_login(self.gestionnaire)
        response = self.client.post(
            reverse("gestion:supprimer_client", args=[self.entreprise.pk]), follow=True
        )
        self.assertContains(response, "suppression impossible")
        self.assertTrue(Client.objects.filter(pk=self.entreprise.pk).exists())
        self.assertEqual(Prestation.objects.count(), 1)

    def test_montant_negatif_refuse_par_formulaire(self):
        form = PrestationForm(data={"client": self.entreprise.pk, "libelle": "Audit",
            "montant": "-1", "date": "2026-10-06", "statut": "PREVUE"})
        self.assertFalse(form.is_valid())
        self.assertIn("montant", form.errors)

    def test_prestation_creation_modification_suppression(self):
        self.client.force_login(self.gestionnaire)
        data = {"client": self.entreprise.pk, "libelle": "Formation",
                "date": "2026-10-06", "montant": "30000", "statut": "PREVUE"}
        self.client.post(reverse("gestion:creer_prestation"), data)
        prestation = Prestation.objects.get()
        data["statut"] = "TERMINEE"
        self.client.post(reverse("gestion:modifier_prestation", args=[prestation.pk]), data)
        prestation.refresh_from_db()
        self.assertEqual(prestation.statut, "TERMINEE")
        url = reverse("gestion:supprimer_prestation", args=[prestation.pk])
        self.client.get(url)
        self.assertEqual(Prestation.objects.count(), 1)
        self.client.post(url)
        self.assertEqual(Prestation.objects.count(), 0)

    def test_total_uniquement_prestations_terminees(self):
        self.client.force_login(self.lecteur)
        url = reverse("gestion:tableau_bord")
        self.assertEqual(self.client.get(url).context["total"], 0)
        for statut, montant in [("TERMINEE", 25000), ("PREVUE", 10000), ("ANNULEE", 9000)]:
            Prestation.objects.create(client=self.entreprise, libelle=statut,
                                      statut=statut, montant=montant)
        self.assertEqual(self.client.get(url).context["total"], Decimal("25000"))

    def test_recherche_pagination_et_404(self):
        self.client.force_login(self.lecteur)
        for n in range(6):
            Client.objects.create(nom=f"Baobab {n}")
        url = reverse("gestion:liste_clients")
        page1 = self.client.get(url, {"q": "Baobab"})
        self.assertEqual(len(page1.context["page"]), 5)
        page2 = self.client.get(url, {"q": "Baobab", "page": 2})
        self.assertEqual(len(page2.context["page"]), 1)
        self.assertNotContains(page2, "Teranga Conseil")
        absent = reverse("gestion:detail_client", args=[99999])
        self.assertEqual(self.client.get(absent).status_code, 404)

    def test_csrf_et_deconnexion_post(self):
        navigateur = Navigateur(enforce_csrf_checks=True)
        navigateur.force_login(self.gestionnaire)
        url = reverse("gestion:creer_client")
        self.assertEqual(navigateur.post(url, {"nom": "Sans jeton"}).status_code, 403)
        navigateur.get(url)
        jeton = navigateur.cookies["csrftoken"].value
        self.assertEqual(navigateur.post(url, {"nom": "Avec jeton",
                                             "csrfmiddlewaretoken": jeton}).status_code, 302)
        self.assertEqual(navigateur.get(reverse("logout")).status_code, 405)
        self.assertEqual(navigateur.post(reverse("logout"),
                         {"csrfmiddlewaretoken": jeton}).status_code, 302)

    def test_templates_echappent_le_html(self):
        self.entreprise.nom = "<script>alert(1)</script>"
        self.entreprise.save()
        self.client.force_login(self.lecteur)
        response = self.client.get(reverse("gestion:detail_client", args=[self.entreprise.pk]))
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>")
