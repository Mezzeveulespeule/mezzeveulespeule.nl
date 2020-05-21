from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django import forms
from django.conf.urls import url
from django.core.mail import send_mail
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render

from mvs.apps.email_form import form_to_email_html
from mvs.models import Aanmelding


class SignupForm(forms.ModelForm):
    title = "Mezzeveulespeule Inschrijfformulier"
    description = """<p>Je kan je hier per gezin inschrijven om mee te doen met Mezzeveulespeule 2020.
                        Inschrijven is dit jaar gratis.</p>"""

    class Meta:
        model = Aanmelding
        fields = [
            'achternaam', 'adres', 'postcode', 'woonplaats',
            'email', 'tel', 'tel2', 'team_naam',
            'kinderen',
            'kind1_naam', 'kind1_leeftijd',
            'kind2_naam', 'kind2_leeftijd',
            'kind3_naam', 'kind3_leeftijd',
            'kind4_naam', 'kind4_leeftijd',
            'kind5_naam', 'kind5_leeftijd',
            'opmerkingen'
        ]

        labels = {
            "achternaam": "Wat is jullie achternaam?",
            "adres": "Wat is jullie adres?",
            "postcode": "Wat is jullie postcode?",
            "woonplaats": "Wat is jullie woonplaats?",
            "email": "Wat is je e-mailadres?",
            "tel": "Op welk telefoonnummer kunnen we jullie bereiken?",
            "tel2": "Op welk tweede telefoonnummer kunnen we jullie bereiken?",
            "team_naam": "Wat is jullie team naam?",
            "kinderen": "Hoeveel kinderen doen in jullie gezin mee?",
            "kind1_naam": "Naam eerste kind",
            "kind1_leeftijd": "Leeftijd eerste kind",
            "kind2_naam": "Naam tweede kind",
            "kind2_leeftijd": "Leeftijd tweede kind",
            "kind3_naam": "Naam derde kind",
            "kind3_leeftijd": "Leeftijd derde kind",
            "kind4_naam": "Naam vierde kind",
            "kind4_leeftijd": "Leeftijd vierde kind",
            "kind5_naam": "Naam vijfde kind",
            "kind5_leeftijd": "Leeftijd vijfde kind",
            "opmerkingen": "Heb je nog opmerkingen?",
        }
        widgets = {"geslacht": forms.RadioSelect}


def signup_view(request):
    form = SignupForm()

    if "thanks" in request.session:
        del request.session["thanks"]
        return render(request, "signup_thanks.html")

    # Handle form submit
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            form.save()

            email_html = form_to_email_html(form)
            message = f"Bedankt voor uw aanmelding, we zullen u spoedig informeren over het programma<br>{email_html}"

            send_mail(
                subject="Inschrijvingsbewijs Mezzeveulespeule",
                message=message,
                from_email="info@mezzeveulespeule.nl",
                recipient_list=[form.cleaned_data['email']],
                fail_silently=True,
                html_message=message,
            )

            # Backup
            send_mail(
                subject="Inschrijving Mezzeveulespeule",
                message=message,
                from_email=form.cleaned_data['email'],
                recipient_list=["info@mezzeveulespeule.nl"],
                fail_silently=True,
                html_message=message,
            )

            request.session["thanks"] = True
            return HttpResponseRedirect(request.path)

    # Laat het formulier zien
    return render(request, "signup.html", {"form": form})


def stats_view(request):
    signups = Aanmelding.objects.count()
    kids = Aanmelding.objects.aggregate(kids=Sum('kinderen'))['kids']

    return render(request, 'content.html', {'content': f"""
    <h1>Inschrijvingen tot nu toe</h1>
    
    <ul>
        <li>Inschrijvingen: {signups}</li>
        <li>Kinderen: {kids}</li>
    </ul>
    """})


@apphook_pool.register
class SignUpHook(CMSApp):
    name = "Aanmeldingsformulier"

    def get_urls(self, page=None, language=None, **kwargs):
        return [
            url("stats", stats_view),
            url("", signup_view),
        ]
