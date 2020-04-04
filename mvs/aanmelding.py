from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django import forms
from django.conf.urls import url
from django.http import Http404, HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import Aanmelding
from .volunteer import VrijwilligerForm, process_volunteer_form


class VrijwilligerInschrijvenForm(VrijwilligerForm):
    description = """
    <p>Zoals elk jaar zijn we weer op zoek naar vrijwilligers om ons te helpen tijdens de dagen.
    We kunnen helaas niet zonder. Hebt u tijd om te helpen? Ook als u maar een dag of een dagdeel kunt, bent u van harte welkom.</p>
    
    <b><a href="/inschrijven/overzicht">Ik heb me al opgegeven / ik wil niet meedoen als vrijwilliger</a></b>
    """


class AanmeldingBasisForm(forms.ModelForm):
    url = ''
    title = 'Mezzeveulespeule Inschrijfformulier'
    description = 'Zijn jullie met meerdere kinderen thuis en willen jullie allemaal meedoen? Dat kan! Vul voor elk kind een apart formulier in.'

    heeft_allergien = forms.BooleanField(
        label='Heeft uw kind allergieën of zijn er bijzonderheden?', required=False)

    description = 'Zijn jullie met meerdere kinderen thuis en willen jullie allemaal meedoen? Dat kan! Vul voor elk kind een apart formulier in. '

    class Meta:
        model = Aanmelding
        fields = ['geslacht', 'voornaam', 'achternaam',
                  'klas', 'adres', 'email', 'tel1', 'tel2',
                  'school']

        labels = {
            'voornaam': 'Wat is zijn/haar voornaam?',
            'achternaam': 'Wat is zijn/haar achternaam?',
            'geslacht': 'Een jongen of meisje?',
            'klas': 'In welke klas zit uw kind?',
            'adres': 'Wat is zijn of haar adres?',
            'email': 'Wat is uw e-mailadres?',
            'tel1': 'Op welk telefoonnummer kunnen we u bereiken voor en tijdens de dagen?',
            'tel2': 'Op welk tweede telefoonnummer kunnen we u in noodgevallen ook bellen?',
            'school': 'Op welke school zit uw kind?',
        }
        widgets = {
            'geslacht': forms.RadioSelect
        }


class AllergienForm(forms.ModelForm):
    url = 'allergieen'
    title = 'Allergieën en bijzonderheden'

    class Meta:
        model = Aanmelding
        fields = ['allergien']
        labels = {
            'allergien': 'Welke allergie heeft uw kind? Of waar moeten we rekening mee houden?'
        }


class GroepsmaatjeForm(forms.ModelForm):
    url = 'groepsmaatje'
    title = 'Groepsmaatje'
    description = ''

    class Meta:
        model = Aanmelding
        fields = ['groepsmaatje', 'groepsmaatje_school']

        labels = {
            'groepsmaatje': 'Bij wie wil uw kind graag in de groep?',
            'groepsmaatje_school': 'Op welke school zit dit groepsmaatje?'
        }


class OvernachtingForm(forms.ModelForm):
    url = 'overnachting'
    title = 'Overnachting voor groep 8'
    description = 'Zit uw kind in groep 8? Dan mag hij voor 2,50 euro extra ook blijven overnachten.'

    class Meta:
        model = Aanmelding
        fields = ['overnachting']
        labels = {
            'overnachting': 'Wil uw kind ook blijven overnachten?'
        }


class ExtraKindForm(forms.ModelForm):
    url = 'extra'
    title = 'Extra kind'
    description = 'Het is mogelijk om meerdere kinderen tegelijkertijd op te geven'

    extra_kind = forms.BooleanField(
        label='Wilt u nog een kind op geven?', required=True)


class OpmerkingenForm(forms.ModelForm):
    url = 'opmerkingen'
    title = 'Opmerkingen of vragen?'

    class Meta:
        model = Aanmelding
        fields = ['opmerkingen']

        labels = {
            'opmerkingen': 'Hebt u nog opmerkingen of vragen?'
        }


def get_form(url, post=None, initial=None):
    """
    Bepaal correcte formulier
    """
    forms = [AanmeldingBasisForm, AllergienForm, GroepsmaatjeForm,
             OvernachtingForm, OpmerkingenForm]

    for form in forms:
        if form.url == url:
            if hasattr(form, 'Meta') and form.Meta.model == Aanmelding:
                return form(post, initial=initial)
            else:
                return form(post)
    raise Http404


# def signedup_view(request):
#     aangemeld_naam = request.session['aangemeld_naam']
#     if request.method == 'POST':
#         if 'nog_een_kind' in request.POST:
#             request.session['aanmelding'] = request.session['zelfde_kind']
#
#         request.session['zelfde_kind'] = {}
#         request.session['aangemeld_naam'] = ''
#         #return redirect_to(AanmeldingBasisForm)
#
#     return render(request, 'signedup.html', {
#         'aangemeld_naam': aangemeld_naam
#     })

def leeg_view(request):
    del request.session['aanmeldingen']
    return HttpResponseRedirect('/inschrijven')

# TODO: Clear session url
# Maak sessie leeg, handige link
#     if url == 'leeg':
#         request.session['aanmeldingen'] = []
#         return redirect_to(AanmeldingBasisForm)

# /inschrijven/review
# /inschrijven/betalen

# /inschrijven/vrijwilliger (nieuwe vrijwilliger, impliciet 1)
# /inschrijven/vrijwiligger/2

def aanmelding_view(request, ordinal, url):
    if ordinal is None:
        ordinal = 1
    else:
        ordinal = int(ordinal)

    if url is None:
        url = ''

    index = ordinal - 1

    # Make sure aanmeldingen exists
    if 'aanmeldingen' not in request.session:
        request.session['aanmeldingen'] = []

    aanmeldingen = request.session['aanmeldingen']

    if index < len(aanmeldingen):
        aanmelding = aanmeldingen[index]
    else:
        if len(aanmeldingen) > 0:
            aanmelding = {
                'achternaam': aanmeldingen[0].get('achternaam', ''),
                'adres': aanmeldingen[0].get('adres', ''),
                'email': aanmeldingen[0].get('email', ''),
                'tel1': aanmeldingen[0].get('tel1', ''),
                'tel2': aanmeldingen[0].get('tel2', ''),
                'school': aanmeldingen[0].get('school', ''),
            }
        else:
            aanmelding = {}

        aanmeldingen.append(aanmelding)
        index = len(aanmeldingen) - 1
        ordinal = len(aanmeldingen)

    # Handle form submit
    if request.method == 'POST':

        # Handle forms
        form = get_form(url, post=request.POST)

        if form.is_valid():
            # Update aanmelding
            for key in form.Meta.fields:
                aanmelding[key] = form.cleaned_data[key]

            # Save
            request.session['aanmeldingen'] = aanmeldingen
            request.session.modified = True

            # Go directly back to overzicht page when this was just an edit
            if 'wijzig' in request.GET:
                return HttpResponseRedirect('/inschrijven/overzicht')

            # Redirect to the next page
            if isinstance(form, AanmeldingBasisForm):
                if form.cleaned_data['heeft_allergien']:
                    return HttpResponseRedirect(f'/inschrijven/{ordinal}/{AllergienForm.url}')
                else:
                    return HttpResponseRedirect(f'/inschrijven/{ordinal}/{GroepsmaatjeForm.url}')

            elif isinstance(form, AllergienForm):
                return HttpResponseRedirect(f'/inschrijven/{ordinal}/{GroepsmaatjeForm.url}')

            elif isinstance(form, GroepsmaatjeForm):
                # Maybe go to Groep 8 page
                if aanmelding['klas'] == '8':
                    return HttpResponseRedirect(f'/inschrijven/{ordinal}/{OvernachtingForm.url}')
                else:
                    return HttpResponseRedirect(f'/inschrijven/{ordinal}/{OpmerkingenForm.url}')

            elif isinstance(form, OvernachtingForm):
                return HttpResponseRedirect(f'/inschrijven/{ordinal}/{OpmerkingenForm.url}')

            elif isinstance(form, OpmerkingenForm):
                return HttpResponseRedirect(f'/inschrijven/extra')
                # print(dict(request.session))
                #
                # aanmelding = Aanmelding(**request.session['aanmelding'])
                # aanmelding.save()
                #
                # # Reset inschrijving
                # zelfde_kind = {}
                # for key in ['achternaam', 'adres', 'email', 'tel1', 'tel2', 'school']:
                #     zelfde_kind[key] = request.session['aanmelding'][key]
                #
                # request.session['aangemeld_naam'] = aanmelding.voornaam + ' ' + aanmelding.achternaam
                # request.session['aanmelding'] = {}
                # request.session['zelfde_kind'] = zelfde_kind
                #
                # # Sla formulier definitief op
                # return HttpResponseRedirect('/inschrijven/aangemeld')

        # Not valid POST? Just show form with errors
    else:
        form = get_form(url, initial=aanmeldingen[index])

        # Personalize form
        if isinstance(form, GroepsmaatjeForm):
            form['groepsmaatje'].label = f"Bij wie wil {aanmelding.get('voornaam', 'uw kind')} graag in de groep?"
        elif isinstance(form, OpmerkingenForm):
            form['opmerkingen'].label = f"Heeft u nog opmerkingen of vragen over de aanmelding van {aanmelding.get('voornaam', 'uw kind')}?"
        elif isinstance(form, AllergienForm):
            form['allergien'].label = f"Welke allergie heeft {aanmelding.get('voornaam', 'uw kind')}? Of waar moeten we rekening mee houden?"
        elif isinstance(form, OvernachtingForm):
            form['overnachting'].label = f"Wil {aanmelding.get('voornaam', 'uw kind')} ook blijven overnachten?"
            form.description = f"Zit {aanmelding.get('voornaam', 'uw kind')} in groep 8? Dan mag hij voor 2,50 euro ook blijven overnachten"


    # Laat het formulier zien
    return render(request, 'aanmelding.html', {
        'form': form
    })


def vrijwilliger_view(request):

    if request.method == 'POST':
        form = VrijwilligerInschrijvenForm(request.POST)

        if form.is_valid():
            # Vrijwilliger opslaan
            # process_volunteer_form(form)

            return render(request, 'aanmelding_vrijwilliger_bedankt.html')
    else:
        if 'aanmeldingen' in request.session and len(request.session['aanmeldingen']) > 0:
            aanmelding = request.session['aanmeldingen'][0]
            initial_data = {
                'achternaam': aanmelding.get('achternaam', ''),
                'adres': aanmelding.get('adres', ''),
                'tel': aanmelding.get('tel1', ''),
                'email': aanmelding.get('email', ''),
            }
        else:
            initial_data = {}

        form = VrijwilligerInschrijvenForm(initial=initial_data)

    return render(request, 'aanmelding.html', {
        'form': form
    })


def overzicht_view(request):

    if request.method == 'POST':
        if 'delete' in request.POST:
            index = int(request.POST.get('delete'))
            request.session['aanmeldingen'].pop(index)
            request.session.modified = True
            return HttpResponseRedirect('/inschrijven/overzicht')

    # Bereken kosten
    kosten = []
    for aanmelding in request.session['aanmeldingen']:
        bedrag = 10
        print(aanmelding['klas'])
        if aanmelding['klas'] == '1' or aanmelding['klas'] == '2':
            print('bedrag=3.5')
            bedrag = 3.5

        kosten.append({'naam': aanmelding['voornaam'], 'bedrag': bedrag})

        if aanmelding.get('overnachting', False):
            kosten.append({'naam': f"Overnachting {aanmelding['voornaam']}", 'bedrag': 2.5})

    return render(request, 'aanmelding_overzicht.html', {
        'aanmeldingen': request.session['aanmeldingen'],
        'kosten': kosten,
        'totaal': sum([regel['bedrag'] for regel in kosten])
    })


def extra_view(request):
    return render(request, 'aanmelding_extra.html', {
        'ordinal': len(request.session['aanmeldingen']) + 1
    })

@apphook_pool.register
class SignUpHook(CMSApp):
    name = 'Aanmeldingsformulier'

    def get_urls(self, page=None, language=None, **kwargs):
        return [
            url(r'^leeg', leeg_view),
            url(r'^overzicht', overzicht_view),
            url(r'^extra', extra_view),
            url(r'^vrijwilliger', vrijwilliger_view),
            url(r'^([0-9]+)?(?:/(.*))?$', aanmelding_view),

        ]
