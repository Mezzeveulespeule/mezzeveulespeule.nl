from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.conf.urls import url
from django.shortcuts import render
from .models import Aanmelding, Vrijwilliger
import os
from django.http import HttpResponseRedirect
import os.path
import random
import re
import html
import mvs.settings as settings
from django import forms
from django.http import Http404
from django.core.mail import send_mail
from django.db.models.query import QuerySet


class Photo(object):
    def __init__(self, folder, file):
        self.folder = folder
        self.file = file

    def get_link(self):
        # Get a link to the photoalbum page

        # Get index
        index = list(map(lambda p: p.file, self.folder.get_photos()
                         )).index(self.file)
        return self.folder.get_link() + '#' + str(index)

    def get_image_link(self):
        return '/media/fotos/' + self.folder.get_folder() + '/' + self.file

    def get_file_link(self):
        return 'fotos/' + self.folder.get_folder() + '/' + self.file

    def is_video(self):
        return self.file.endswith('.mp4')


class PhotosFolder(object):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def get_directory(self):
        if self.parent is None:
            return settings.MEDIA_ROOT + '/fotos'
        else:
            return self.parent.get_directory() + '/' + self.name

    def get_breadcrumbs(self):
        if self.parent is None:
            return [self]
        else:
            breadcrumbs = self.parent.get_breadcrumbs()
            breadcrumbs.append(self)
            return breadcrumbs

    def get_name(self):
        return self.name.split('.', 1)[1].strip()

    def get_link(self):
        if self.parent is None:
            return '/fotos'
        else:
            return self.parent.get_link() + '/' + self.get_slug()

    def get_folder(self):
        if self.parent.parent is None:
            return self.name
        else:
            return self.parent.get_folder() + '/' + self.name

    def get_slug(self):
        name = self.get_name()
        name = name.replace('\'', '').lower()
        name = re.sub(r'[^a-z0-9]+', '-', name).strip('-')
        return name

    def get_subfolders(self):
        subfolders = []
        directory = self.get_directory()
        for dirname in sorted(os.listdir(directory)):
            if not dirname.startswith('.') and os.path.isdir(directory + '/' + dirname):
                subfolders.append(PhotosFolder(self, dirname))

        return subfolders

    def has_subfolders(self):
        return len(self.get_subfolders()) > 0

    def get_photos(self):
        return [Photo(self, filename) for filename in sorted(os.listdir(self.get_directory())) if filename.endswith('.jpg') or filename.endswith('.mp4')]

    def get_random_photo(self):
        if self.has_subfolders():
            return random.choice(self.get_subfolders()).get_random_photo()
        else:
            return random.choice(self.get_photos())

    def get_subfolder_for_slug(self, slug):
        for child in self.get_subfolders():
            if child.get_slug() == slug:
                return child

        return None

    @classmethod
    def get_root(cls):
        return PhotosFolder(None, '1. Foto\'s')

    @classmethod
    def get_for_url(cls, url):
        root = PhotosFolder.get_root()
        url_parts = url.split('/')

        folder = root
        for part in url_parts:
            folder = folder.get_subfolder_for_slug(part)
            if folder is None:
                return None

        return folder


def fotos_view(request, url):
    folder = PhotosFolder.get_for_url(url)
    return render(request, 'fotos.html', {'folder': folder})


@apphook_pool.register
class FotosHook(CMSApp):
    name = 'Fotos'

    def get_urls(self, page=None, language=None, **kwargs):

        # replace this with the path to your application's URLs module
        return [
            url(r'^(.+)', fotos_view),
        ]


class VrijwilligerVraagForm(forms.Form):
    url = 'vrijwilliger'
    title = 'Vrijwilligers'
    description = 'Zoals elk jaar zijn we weer op zoek naar vrijwilligers om ons te helpen tijdens de dagen. We kunnen helaas niet zonder. Hebt u tijd om te helpen? Ook als u maar een dag of een dagdeel kunt, bent u van harte welkom.'

    aanmelden = forms.ChoiceField(label='Kunt u komen helpen?', choices=[
        ('ja', 'Ja'),
        ('nee', 'Nee'),
        ('nee', 'Ik heb me al aangemeld'),
    ], widget=forms.RadioSelect)

class VrijwilligerForm(forms.ModelForm):
    title = 'Vrijwilligers'

    class Meta:
        model = Vrijwilliger
        exclude = []

        labels = {
            'tel': 'Telefoonnummer 1',
            'tel2': 'Telefoonnummer 2',
            'ehbo': 'Heeft u een EHBO diploma?',
            'stage': 'Bent u vrijwilliger voor een maatschappelijke stage?',
            'dagen': 'Op welke dagen zou u (eventueel) kunnen komen helpen?',
            'taken': 'Hebt u een voorkeur voor een bepaalde taak?',
            'eigen_kind': 'Indien u een groep wilt begeleiden, wilt u uw eigen kind in de groep? (Geef de naam van de kinderen die u in de groep wil:)',
            'opmerkingen': 'Hebt u nog andere opmerkingen?'
        }

        widgets = {
            'dagen': forms.CheckboxSelectMultiple,
            'taken': forms.CheckboxSelectMultiple,
            'geboortedatum': forms.DateInput(attrs={'type': 'date'})
        }

class VrijwilligerInschrijvenForm(VrijwilligerForm):
    url = 'vrijwilliger/aanmelden'

    nog_een = forms.BooleanField(
        label='Wilt u nog een vrijwilliger opgeven?', required=False)

class AanmeldingBasisForm(forms.ModelForm):
    url = ''
    title = 'Mezzeveulespeule Inschrijfformulier'
    description = 'Zijn jullie met meerdere kinderen thuis en willen jullie allemaal meedoen? Dat kan! Vul voor elk kind een apart formulier in.'

    heeft_allergien = forms.BooleanField(
        label='Heeft uw kind allergieën of zijn er bijzonderheden?', required=False)

    description = 'Zijn jullie met meerdere kinderen thuis en willen jullie allemaal meedoen? Dat kan! Vul voor elk kind een apart formulier in. '

    class Meta:
        model = Aanmelding
        fields = ['voornaam', 'achternaam', 'geslacht',
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
    url = 'allergien'
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
    description = 'Zit uw kind is groep 8? Dan mag hij voor 2,50 euro extra ook blijven overnachten. '

    class Meta:
        model = Aanmelding
        fields = ['overnachting']
        labels = {
            'overnachting': 'Wil uw kind ook blijven overnachten?'
        }


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
    forms = [VrijwilligerInschrijvenForm, VrijwilligerVraagForm,
             AanmeldingBasisForm, AllergienForm, GroepsmaatjeForm,
             OvernachtingForm, OpmerkingenForm]

    for form in forms:
        if form.url == url:
            if hasattr(form, 'Meta') and form.Meta.model == Aanmelding:
                return form(post, initial=initial)
            else:
                return form(post)
    raise Http404


def redirect_to(form):
    return HttpResponseRedirect('/inschrijven/{0}'.format(form.url))


def signedup_view(request):
    aangemeld_naam = request.session['aangemeld_naam']
    if request.method == 'POST':
        if 'nog_een_kind' in request.POST:
            request.session['aanmelding'] = request.session['zelfde_kind']

        request.session['zelfde_kind'] = {}
        request.session['aangemeld_naam'] = ''
        return redirect_to(AanmeldingBasisForm)

    return render(request, 'signedup.html', {
        'aangemeld_naam': aangemeld_naam
    })


def signup_view(request, url):

    # Make sure aanmelding exists
    if 'aanmelding' not in request.session:
        request.session['aanmelding'] = {}

    # Maak sessie leeg, handige link
    if url == 'leeg':
        request.session['aanmelding'] = {}
        return redirect_to(AanmeldingBasisForm)

    # Handle einde

    if request.method == 'POST':
        form = get_form(url, post=request.POST)

        if form.is_valid():
            # Copy all values into session
            if hasattr(form, 'Meta') and form.Meta.model == Aanmelding:
                for key in form.Meta.fields:
                    request.session['aanmelding'][key] = form.cleaned_data[key]

            request.session.modified = True

            # Redirect to the next page
            if isinstance(form, AanmeldingBasisForm):
                if form.cleaned_data['heeft_allergien']:
                    return redirect_to(AllergienForm)
                else:
                    return redirect_to(GroepsmaatjeForm)

            elif isinstance(form, AllergienForm):
                return redirect_to(GroepsmaatjeForm)

            elif isinstance(form, GroepsmaatjeForm):
                # Maybe go to Groep 8 page
                if request.session['aanmelding']['klas'] == '8':
                    return redirect_to(OvernachtingForm)
                else:
                    return redirect_to(VrijwilligerVraagForm)

            elif isinstance(form, OvernachtingForm):
                return redirect_to(VrijwilligerVraagForm)

            elif isinstance(form, VrijwilligerVraagForm):
                if form.cleaned_data['aanmelden'] == 'ja':
                    return redirect_to(VrijwilligerInschrijvenForm)
                else:
                    return redirect_to(OpmerkingenForm)
            elif isinstance(form, VrijwilligerInschrijvenForm):

                # Save form
                form.save()
                if form.cleaned_data['nog_een']:
                    # TODO: Iets laten weten?
                    return redirect_to(VrijwilligerInschrijvenForm)
                else:
                    return redirect_to(OpmerkingenForm)

            elif isinstance(form, OpmerkingenForm):
                print(dict(request.session))

                aanmelding = Aanmelding(**request.session['aanmelding'])
                aanmelding.save()

                # Reset inschrijving
                zelfde_kind = {}
                for key in ['achternaam', 'adres', 'email', 'tel1', 'tel2', 'school']:
                    zelfde_kind[key] = request.session['aanmelding'][key]

                request.session['aangemeld_naam'] = aanmelding.voornaam + ' ' + aanmelding.achternaam
                request.session['aanmelding'] = {}
                request.session['zelfde_kind'] = zelfde_kind

                # Sla formulier definitief op
                return HttpResponseRedirect('/inschrijven/aangemeld')

        # Not valid POST? Just show errors
    else:
        form = get_form(url, initial=request.session['aanmelding'])

    # Laat het formulier zien
    return render(request, 'signup.html', {
        'form': form
    })


@apphook_pool.register
class SignUpHook(CMSApp):
    name = 'Aanmeldingsformulier'

    def get_urls(self, page=None, language=None, **kwargs):

        # replace this with the path to your application's URLs module
        return [
            url(r'^aangemeld', signedup_view),
            url(r'^(.*)', signup_view),

        ]


@apphook_pool.register
class VolunteerHook(CMSApp):
    name = 'Vrijwilligers'

    def get_urls(self, page=None, language=None, **kwargs):
        return [url(r'', self.view)]

    def view(self, request):
        # Show thank you message
        if 'thanks' in request.session:
            del request.session['thanks']
            return render(request, 'vrijwilliger_thanks.html')

        if request.method == 'POST':
            # Validate form
            form = VrijwilligerForm(request.POST)

            if form.is_valid():
                form.save()

                # Construct overview
                email_html = """
                <style>
                th {
                    text-align: right;
                }
                th, td {
                    padding: 5px;
                }
                </style>
                <table>
                """

                for field in form:
                    data = form.cleaned_data[field.name]

                    # Make human readable
                    if isinstance(data, bool):
                        print(data)
                        data = 'Ja' if data else 'Nee'

                    elif isinstance(data, QuerySet):
                        data = ', '.join(map(str, data))
                    else:
                        data = str(data)

                    email_html += '<tr><th>' + field.label + ':</th><td>' + html.escape(data) + '<td></tr>'

                email_html += '</table>'

                # Send to organization
                send_mail('Nieuwe Vrijwilliger',
                          email_html,
                          'info@mezzeveulespeule.nl',
                          ['vrijwilligers@mezzeveulespeule.nl'],
                          html_message=email_html)

                # Send copy to volunteer
                volunteer_email = form.cleaned_data['email']
                send_mail('Aanmelding Vrijwilliger',
                          'Bedankt voor uw aanmelding!',
                          'info@mezzeveulespeule.nl',
                          [volunteer_email],
                          html_message='<h1>Aanmelding Vrijwillliger</h1>' +
                          '<p>Bedankt voor uw aanmelding!</p>' +
                          email_html)

                request.session['thanks'] = True
                return HttpResponseRedirect(request.path)
        else:
            form = VrijwilligerForm()

        # Show form
        return render(request, 'vrijwilliger.html', {
            'form': form
        })
