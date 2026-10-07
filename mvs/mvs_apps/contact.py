from email.message import EmailMessage

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django import forms
from django.urls import re_path
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render

from mvs.mvs_apps.email_form import form_to_email_html


class ContactForm(forms.Form):
    first_name = forms.CharField(label='Voornaam', max_length=100)
    last_name = forms.CharField(label='Achternaam', max_length=100)
    email = forms.EmailField(label='E-mailadres')
    telephone = forms.CharField(label='Telefoonnummer')
    subject = forms.CharField(label='Onderwerp', max_length=100)
    message = forms.CharField(label='Bericht', widget=forms.Textarea)


@apphook_pool.register
class ContactHook(CMSApp):
    name = "Contactformulier"

    def get_urls(self, page=None, language=None, **kwargs):
        return [re_path(r"", self.view)]

    @staticmethod
    def view(request):
        form = ContactForm()
        if request.method == 'POST':
            form = ContactForm(request.POST)

            if form.is_valid():
                email_html = form_to_email_html(form)

                msg = EmailMultiAlternatives(
                    subject=form.cleaned_data['subject'],
                    body=email_html,
                    from_email="noreply@paulwagener.nl",
                    to=["info@mezzeveulespeule.nl"],
                    reply_to=[form.cleaned_data['email']],
                )
                msg.attach_alternative(email_html, "text/html")
                msg.send()

                return render(request, "contact_thanks.html")

        return render(request, "contact.html", {"form": form})
