from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django import forms
from django.conf.urls import url
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render

from mvs.models import Aanmelding, Vrijwilliger


class VrijwilligerVraagForm(forms.Form):
    url = "vrijwilliger"
    title = "Vrijwilligers"
    description = "Zoals elk jaar zijn we weer op zoek naar vrijwilligers om ons te helpen tijdens de dagen. We kunnen helaas niet zonder. Hebt u tijd om te helpen? Ook als u maar een dag of een dagdeel kunt, bent u van harte welkom."

    aanmelden = forms.ChoiceField(
        label="Kunt u komen helpen?",
        choices=[
            ("ja", "Ja"),
            ("nee", "Nee"),
            ("nee", "Ik heb me al aangemeld"),
        ],
        widget=forms.RadioSelect,
    )


class VrijwilligerForm(forms.ModelForm):
    title = "Vrijwilligers"

    class Meta:
        model = Vrijwilliger
        exclude = []

        labels = {
            "tel": "Telefoonnummer 1",
            "tel2": "Telefoonnummer 2",
            "ehbo": "Heeft u een EHBO diploma?",
            "stage": "Bent u vrijwilliger voor een maatschappelijke stage?",
            "dagen": "Op welke dagen zou u (eventueel) kunnen komen helpen?",
            "taken": "Hebt u een voorkeur voor een bepaalde taak?",
            "eigen_kind": "Indien u een groep wilt begeleiden, wilt u uw eigen kind in de groep? (Geef de naam van de kinderen die u in de groep wil:)",
            "opmerkingen": "Hebt u nog andere opmerkingen?",
        }

        widgets = {
            "dagen": forms.CheckboxSelectMultiple,
            "taken": forms.CheckboxSelectMultiple,
            "geboortedatum": forms.DateInput(attrs={"type": "date"}),
        }


class VrijwilligerInschrijvenForm(VrijwilligerForm):
    url = "vrijwilliger/aanmelden"

    nog_een = forms.BooleanField(
        label="Wilt u nog een vrijwilliger opgeven?", required=False
    )


class AanmeldingBasisForm(forms.ModelForm):
    url = ""
    title = "Mezzeveulespeule Inschrijfformulier"
    heeft_allergien = forms.BooleanField(
        label="Heeft uw kind allergieën of zijn er bijzonderheden?", required=False
    )

    description = "Zijn jullie met meerdere kinderen thuis en willen jullie allemaal meedoen? Dat kan! Vul voor elk kind een apart formulier in. "

    class Meta:
        model = Aanmelding
        fields = [
            "voornaam",
            "achternaam",
            "geslacht",
            "klas",
            "adres",
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
            "email": "Wat is uw e-mailadres?",
            "tel1": "Op welk telefoonnummer kunnen we u bereiken voor en tijdens de dagen?",
            "tel2": "Op welk tweede telefoonnummer kunnen we u in noodgevallen ook bellen?",
            "school": "Op welke school zit uw kind?",
        }
        widgets = {"geslacht": forms.RadioSelect}


class AllergienForm(forms.ModelForm):
    url = "allergien"
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
    description = "Zit uw kind is groep 8? Dan mag hij voor 3,50 euro extra ook blijven overnachten. "

    class Meta:
        model = Aanmelding
        fields = ["overnachting"]
        labels = {"overnachting": "Wil uw kind ook blijven overnachten?"}


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
        VrijwilligerInschrijvenForm,
        VrijwilligerVraagForm,
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


def redirect_to(form):
    return HttpResponseRedirect("/inschrijven/{0}".format(form.url))


def signedup_view(request):
    aangemeld_naam = request.session["aangemeld_naam"]
    if request.method == "POST":
        if "nog_een_kind" in request.POST:
            request.session["aanmelding"] = request.session["zelfde_kind"]

        request.session["zelfde_kind"] = {}
        request.session["aangemeld_naam"] = ""
        return redirect_to(AanmeldingBasisForm)

    return render(request, "signedup.html", {"aangemeld_naam": aangemeld_naam})


def signup_view(request, url):

    # Make sure aanmelding exists
    if "aanmelding" not in request.session:
        request.session["aanmelding"] = {}

    # Maak sessie leeg, handige link
    if url == "leeg":
        request.session["aanmelding"] = {}
        return redirect_to(AanmeldingBasisForm)

    # Handle einde

    if request.method == "POST":
        form = get_form(url, post=request.POST)

        if form.is_valid():
            # Copy all values into session
            if hasattr(form, "Meta") and form.Meta.model == Aanmelding:
                for key in form.Meta.fields:
                    request.session["aanmelding"][key] = form.cleaned_data[key]

            request.session.modified = True

            # Redirect to the next page
            if isinstance(form, AanmeldingBasisForm):
                if form.cleaned_data["heeft_allergien"]:
                    return redirect_to(AllergienForm)
                else:
                    return redirect_to(GroepsmaatjeForm)

            elif isinstance(form, AllergienForm):
                return redirect_to(GroepsmaatjeForm)

            elif isinstance(form, GroepsmaatjeForm):
                # Maybe go to Groep 8 page
                if request.session["aanmelding"]["klas"] == "8":
                    return redirect_to(OvernachtingForm)
                else:
                    return redirect_to(VrijwilligerVraagForm)

            elif isinstance(form, OvernachtingForm):
                return redirect_to(VrijwilligerVraagForm)

            elif isinstance(form, VrijwilligerVraagForm):
                if form.cleaned_data["aanmelden"] == "ja":
                    return redirect_to(VrijwilligerInschrijvenForm)
                else:
                    return redirect_to(OpmerkingenForm)
            elif isinstance(form, VrijwilligerInschrijvenForm):

                # Save form
                form.save()
                if form.cleaned_data["nog_een"]:
                    # TODO: Iets laten weten?
                    return redirect_to(VrijwilligerInschrijvenForm)
                else:
                    return redirect_to(OpmerkingenForm)

            elif isinstance(form, OpmerkingenForm):
                print(dict(request.session))

                aanmelding = Aanmelding(**request.session["aanmelding"])
                aanmelding.save()

                # Reset inschrijving
                zelfde_kind = {}
                for key in ["achternaam", "adres", "email", "tel1", "tel2", "school"]:
                    zelfde_kind[key] = request.session["aanmelding"][key]

                request.session["aangemeld_naam"] = (
                    aanmelding.voornaam + " " + aanmelding.achternaam
                )
                request.session["aanmelding"] = {}
                request.session["zelfde_kind"] = zelfde_kind

                # Sla formulier definitief op
                return HttpResponseRedirect("/inschrijven/aangemeld")

        # Not valid POST? Just show errors
    else:
        if url == VrijwilligerInschrijvenForm.url:
            aanmelding = request.session["aanmelding"]
            form = VrijwilligerInschrijvenForm(
                initial={
                    "achternaam": aanmelding["achternaam"],
                    "adres": aanmelding["adres"],
                    "tel": aanmelding["tel1"],
                    "email": aanmelding["email"],
                }
            )
        else:
            form = get_form(url, initial=request.session["aanmelding"])

    # Laat het formulier zien
    return render(request, "signup.html", {"form": form})


@apphook_pool.register
class SignUpHook(CMSApp):
    name = "Aanmeldingsformulier"

    def get_urls(self, page=None, language=None, **kwargs):

        # replace this with the path to your application's URLs module
        return [
            url(r"^aangemeld", signedup_view),
            url(r"^(.*)", signup_view),
        ]
