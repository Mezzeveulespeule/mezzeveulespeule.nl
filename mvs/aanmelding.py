from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django import forms
from django.conf.urls import url
from django.http import Http404, HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.mail import send_mail

from .models import Aanmelding
from .volunteer import VrijwilligerForm, process_volunteer_form
from mollie.api.client import Client
from .secrets import MOLLIE_API_KEY

mollie_client = Client()
mollie_client.set_api_key(MOLLIE_API_KEY)


class VrijwilligerInschrijvenForm(VrijwilligerForm):
    description = """
    <p>Zoals elk jaar zijn we weer op zoek naar vrijwilligers om ons te helpen tijdens de dagen.
    Zonder vrijwilligers kunnen we de dagen niet organiseren. Hebt u tijd om te helpen? Ook als u maar een dag of een dagdeel kunt, bent u van harte welkom.</p>

    <b><a href="/inschrijven/overzicht">Ik heb me al opgegeven / ik wil niet meedoen als vrijwilliger</a></b>
    """


class AanmeldingBasisForm(forms.ModelForm):
    url = ""
    title = "Mezzeveulespeule Inschrijfformulier"
    description = """<p>Zijn jullie met meerdere kinderen thuis en willen jullie allemaal meedoen? Dat kan! Vul voor elk kind een apart formulier in. Bepaalde informatie wordt al voor u ingevuld.</p>

    <p>Aan het eind kunt u in één keer met iDeal alles betalen en is de aanmelding meteen afgerond</p>

    <table cellspacing=7>
      <tr>
        <td>Groep 1/2</td>
        <td>€3,50</td>
      </tr>
      <tr>
        <td>Groep 3-8</td>
        <td>€10,00</td>
      </tr>
      <tr>
        <td>Overnachting groep 8</td>
        <td>+€2,50</td>
      </tr>
    </table>
    """

    heeft_allergien = forms.BooleanField(
        label="Heeft uw kind allergieën of zijn er bijzonderheden?", required=False
    )

    class Meta:
        model = Aanmelding
        fields = [
            "geslacht",
            "voornaam",
            "achternaam",
            "klas",
            "adres",
            "postcode",
            "woonplaats",
            "email",
            "tel1",
            "tel2",
            "school",
        ]

        labels = {
            "voornaam": "Wat is zijn/haar voornaam?",
            "achternaam": "Wat is zijn/haar achternaam?",
            "geslacht": "Een jongen of meisje?",
            "klas": "In welke klas zit uw kind?",
            "adres": "Wat is zijn of haar adres?",
            "postcode": "Wat is zijn of haar postcode?",
            "woonplaats": "Wat is zijn of haar woonplaats?",
            "email": "Wat is uw e-mailadres?",
            "tel1": "Op welk telefoonnummer kunnen we u bereiken voor en tijdens de dagen?",
            "tel2": "Op welk tweede telefoonnummer kunnen we u in noodgevallen ook bellen?",
            "school": "Op welke school zit uw kind?",
        }
        widgets = {"geslacht": forms.RadioSelect}


class AllergienForm(forms.ModelForm):
    url = "allergieen"
    title = "Allergieën en bijzonderheden"

    class Meta:
        model = Aanmelding
        fields = ["allergien"]
        labels = {
            "allergien": "Welke allergie heeft uw kind? Of waar moeten we rekening mee houden?"
        }


class GroepsmaatjeForm(forms.ModelForm):
    url = "groepsmaatje"
    title = "Groepsmaatje"
    description = ""

    class Meta:
        model = Aanmelding
        fields = ["groepsmaatje", "groepsmaatje_school"]

        labels = {
            "groepsmaatje": "Bij wie wil uw kind graag in de groep?",
            "groepsmaatje_school": "Op welke school zit dit groepsmaatje?",
        }


class OvernachtingForm(forms.ModelForm):
    url = "overnachting"
    title = "Overnachting voor groep 8"
    description = "Zit uw kind in groep 8? Dan mag hij voor 2,50 euro extra ook blijven overnachten."

    class Meta:
        model = Aanmelding
        fields = ["overnachting"]
        labels = {"overnachting": "Wil uw kind ook blijven overnachten?"}


class ExtraKindForm(forms.ModelForm):
    url = "extra"
    title = "Extra kind"
    description = "Het is mogelijk om meerdere kinderen tegelijkertijd op te geven"

    extra_kind = forms.BooleanField(
        label="Wilt u nog een kind op geven?", required=True
    )


class OpmerkingenForm(forms.ModelForm):
    url = "opmerkingen"
    title = "Opmerkingen of vragen?"

    class Meta:
        model = Aanmelding
        fields = ["opmerkingen"]

        labels = {"opmerkingen": "Hebt u nog opmerkingen of vragen?"}


def get_form(url, post=None, initial=None):
    """
    Bepaal correcte formulier
    """
    forms = [
        AanmeldingBasisForm,
        AllergienForm,
        GroepsmaatjeForm,
        OvernachtingForm,
        OpmerkingenForm,
    ]

    for form in forms:
        if form.url == url:
            if hasattr(form, "Meta") and form.Meta.model == Aanmelding:
                return form(post, initial=initial)
            else:
                return form(post)
    raise Http404


def leeg_view(request):
    del request.session["aanmeldingen"]
    return HttpResponseRedirect("/inschrijven")


def aanmelding_view(request, ordinal, url):
    if ordinal is None:
        ordinal = 1
    else:
        ordinal = int(ordinal)

    if url is None:
        url = ""

    index = ordinal - 1

    # Make sure aanmeldingen exists
    if "aanmeldingen" not in request.session:
        request.session["aanmeldingen"] = []

    aanmeldingen = request.session["aanmeldingen"]

    if index < len(aanmeldingen):
        aanmelding = aanmeldingen[index]
    else:
        if len(aanmeldingen) > 0:
            aanmelding = {
                "achternaam": aanmeldingen[0].get("achternaam", ""),
                "adres": aanmeldingen[0].get("adres", ""),
                "postcode": aanmeldingen[0].get("postcode", ""),
                "woonplaats": aanmeldingen[0].get("woonplaats", ""),
                "email": aanmeldingen[0].get("email", ""),
                "tel1": aanmeldingen[0].get("tel1", ""),
                "tel2": aanmeldingen[0].get("tel2", ""),
                "school": aanmeldingen[0].get("school", ""),
            }
        else:
            aanmelding = {"woonplaats": "Bladel"}

        aanmeldingen.append(aanmelding)
        index = len(aanmeldingen) - 1
        ordinal = len(aanmeldingen)

    # Handle form submit
    if request.method == "POST":

        # Handle forms
        form = get_form(url, post=request.POST)

        if form.is_valid():
            # Update aanmelding
            for key in form.Meta.fields:
                aanmelding[key] = form.cleaned_data[key]

            # Save
            request.session["aanmeldingen"] = aanmeldingen
            request.session.modified = True

            # Go directly back to overzicht page when this was just an edit
            if "wijzig" in request.GET:
                return HttpResponseRedirect("/inschrijven/overzicht")

            # Redirect to the next page
            if isinstance(form, AanmeldingBasisForm):
                if form.cleaned_data["heeft_allergien"]:
                    return HttpResponseRedirect(
                        f"/inschrijven/{ordinal}/{AllergienForm.url}"
                    )
                else:
                    return HttpResponseRedirect(
                        f"/inschrijven/{ordinal}/{GroepsmaatjeForm.url}"
                    )

            elif isinstance(form, AllergienForm):
                return HttpResponseRedirect(
                    f"/inschrijven/{ordinal}/{GroepsmaatjeForm.url}"
                )

            elif isinstance(form, GroepsmaatjeForm):
                # Maybe go to Groep 8 page
                if aanmelding["klas"] == "8":
                    return HttpResponseRedirect(
                        f"/inschrijven/{ordinal}/{OvernachtingForm.url}"
                    )
                else:
                    return HttpResponseRedirect(
                        f"/inschrijven/{ordinal}/{OpmerkingenForm.url}"
                    )

            elif isinstance(form, OvernachtingForm):
                return HttpResponseRedirect(
                    f"/inschrijven/{ordinal}/{OpmerkingenForm.url}"
                )

            elif isinstance(form, OpmerkingenForm):
                return HttpResponseRedirect(f"/inschrijven/extra")

        # Not valid POST? Just show form with errors
    else:
        form = get_form(url, initial=aanmeldingen[index])

        # Personalize form
        if isinstance(form, GroepsmaatjeForm):
            form[
                "groepsmaatje"
            ].label = f"Bij wie wil {aanmelding.get('voornaam', 'uw kind')} graag in de groep?"
        elif isinstance(form, OpmerkingenForm):
            form["opmerkingen"].label = (
                "Heeft u nog opmerkingen of vragen "
                f"over de aanmelding van {aanmelding.get('voornaam', 'uw kind')}?"
            )
        elif isinstance(form, AllergienForm):
            form["allergien"].label = (
                f"Welke allergie heeft {aanmelding.get('voornaam', 'uw kind')}?"
                f" Of waar moeten we rekening mee houden?"
            )
        elif isinstance(form, OvernachtingForm):
            form["overnachting"].label = (
                f"Wil {aanmelding.get('voornaam', 'uw kind')} "
                "ook blijven overnachten?"
            )
            form.description = (
                f"Zit {aanmelding.get('voornaam', 'uw kind')} in groep 8? "
                "Dan mag hij voor 2,50 euro ook blijven overnachten"
            )

    # Laat het formulier zien
    return render(request, "aanmelding.html", {"form": form})


def vrijwilliger_view(request):

    if request.method == "POST":
        form = VrijwilligerInschrijvenForm(request.POST)

        if form.is_valid():
            # Vrijwilliger opslaan
            process_volunteer_form(form)

            return render(request, "aanmelding_vrijwilliger_bedankt.html")
    else:
        if (
            "aanmeldingen" in request.session
            and len(request.session["aanmeldingen"]) > 0
        ):
            aanmelding = request.session["aanmeldingen"][0]
            initial_data = {
                "achternaam": aanmelding.get("achternaam", ""),
                "adres": aanmelding.get("adres", ""),
                "postcode": aanmelding.get("postcode", ""),
                "woonplaats": aanmelding.get("woonplaats", ""),
                "tel": aanmelding.get("tel1", ""),
                "tel2": aanmelding.get("tel2", ""),
                "email": aanmelding.get("email", ""),
            }
        else:
            initial_data = {}

        form = VrijwilligerInschrijvenForm(initial=initial_data)

    return render(request, "aanmelding.html", {"form": form})


def overzicht_view(request):
    if "aanmeldingen" not in request.session:
        return HttpResponseRedirect("/inschrijven")

    # Bereken kosten
    kosten = []
    for aanmelding in request.session["aanmeldingen"]:
        bedrag = 10
        if aanmelding["klas"] == "1" or aanmelding["klas"] == "2":
            bedrag = 3.5

        kosten.append({"naam": aanmelding["voornaam"], "bedrag": bedrag})

        if aanmelding.get("overnachting", False):
            kosten.append(
                {"naam": f"Overnachting {aanmelding['voornaam']}", "bedrag": 2.5}
            )

    totaal = sum([regel["bedrag"] for regel in kosten])

    if request.method == "POST":
        if "delete" in request.POST:
            index = int(request.POST.get("delete"))
            request.session["aanmeldingen"].pop(index)
            request.session.modified = True
            return HttpResponseRedirect("/inschrijven/overzicht")

        if "betalen" in request.POST:

            # Maak de betaling 'echt'

            payment = maak_betaling(request, totaal)

            # Sla de aanmelding op in de database
            for aanmelding_data in request.session["aanmeldingen"]:
                aanmelding = Aanmelding(**aanmelding_data)
                aanmelding.payment_id = payment.id
                aanmelding.save()

            return HttpResponseRedirect(payment.checkout_url)

    return render(
        request,
        "aanmelding_overzicht.html",
        {
            "aanmeldingen": request.session["aanmeldingen"],
            "kosten": kosten,
            "totaal": totaal,
        },
    )


def extra_view(request):
    return render(
        request,
        "aanmelding_extra.html",
        {"ordinal": len(request.session["aanmeldingen"]) + 1},
    )


def betaling_view(request):
    if "betaling" not in request.session:
        return HttpResponseRedirect("/inschrijven/overzicht")

    payment = mollie_client.payments.get(request.session["betaling"])
    aanmeldingen = Aanmelding.objects.filter(payment_id=payment.id)

    if request.method == "POST":
        if "leeg" in request.POST:
            del request.session["betaling"]
            del request.session["aanmeldingen"]
            return HttpResponseRedirect("/inschrijven")

        if "retry" in request.POST:
            payment = maak_betaling(request, float(payment.amount["value"]))

            for aanmelding in aanmeldingen:
                aanmelding.payment_id = payment.id
                aanmelding.save()

            return HttpResponseRedirect(payment.checkout_url)

    if payment.is_paid():
        del request.session["aanmeldingen"]
        del request.session["betaling"]

        for aanmelding in aanmeldingen:
            aanmelding.heeft_betaald = True
            aanmelding.save()

        # Send confirmation e-mail
        for aanmelding in aanmeldingen:
            email_html = f"""
                            <style>
                            th {{
                                text-align: right;
                            }}
                            th, td {{
                                padding: 5px;
                            }}
                            </style>
                            <h1>Bevestiging inschrijving Mezzeveulespeule</h1>
                            <table>
                              <tr><th>Voornaam</th><td>{aanmelding.voornaam}</td></tr>
                              <tr><th>Achternaam</th><td>{aanmelding.achternaam}</td></tr>
                              <tr><th>Geslacht</th><td>{aanmelding.geslacht}</td></tr>
                              <tr><th>Klas</th><td>Groep {aanmelding.klas}</td></tr>
                              <tr><th>Adres</th><td>{aanmelding.adres}</td></tr>
                              <tr><th>Postcode</th><td>{aanmelding.postcode}</td></tr>
                              <tr><th>Woonplaats</th><td>{aanmelding.woonplaats}</td></tr>
                              <tr><th>E-mail</th><td>{aanmelding.email}</td></tr>
                              <tr><th>Telefoonnummer 1</th><td>{aanmelding.tel1}</td></tr>
                              <tr><th>Telefoonnummer 2</th><td>{aanmelding.tel2}</td></tr>
                              <tr><th>Allergieën</th><td>{aanmelding.allergien}</td></tr>
                              <tr><th>Groepsmaatje</th><td>{aanmelding.groepsmaatje}</td></tr>
                              <tr><th>School groepsmaatje</th><td>{aanmelding.groepsmaatje_school}</td></tr>
                              {"<tr><td>Overnachting</th><td>Ja</td></tr>" if aanmelding.overnachting else ""}
                              <tr><td>Opmerkingen / vragen</th><td>{aanmelding.opmerkingen}</td></tr>
                            </table>
                              """
            # Send to user
            send_mail(
                "Inschrijving Mezzeveulespeule",
                "",
                "info@mezzeveulespeule.nl",
                [aanmelding.email],
                fail_silently=True,
                html_message=email_html,
            )

            # Send to organization
            send_mail(
                "Inschrijving Mezzeveulespeule",
                "",
                "vrijwilligers@mezzeveulespeule.nl",
                ["vrijwilligers@mezzeveulespeule.nl"],
                fail_silently=True,
                html_message="(Deze email is bedoeld als backup, alle data komt ook nog als Excel bestand)"
                + email_html,
            )

        return render(request, "aanmelding_aangemeld.html")
    else:
        return render(request, "aanmelding_betaling_mislukt.html")


def maak_betaling(request, bedrag: float) -> str:
    payment = mollie_client.payments.create(
        {
            "amount": {"currency": "EUR", "value": "{0:.2f}".format(bedrag)},
            "description": "Inschrijfgeld Mezzeveulespeule",
            "redirectUrl": request.build_absolute_uri("/inschrijven/betaling"),
        }
    )

    request.session["betaling"] = payment.id

    return payment


@apphook_pool.register
class SignUpHook(CMSApp):
    name = "Aanmeldingsformulier"

    def get_urls(self, page=None, language=None, **kwargs):
        return [
            url(r"^leeg", leeg_view),
            url(r"^overzicht", overzicht_view),
            url(r"^extra", extra_view),
            url(r"^vrijwilliger", vrijwilliger_view),
            url(r"^betaling", betaling_view),
            url(r"^([0-9]+)?(?:/(.*))?$", aanmelding_view),
        ]
