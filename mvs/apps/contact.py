from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django import forms
from django.conf.urls import url
from django.core.mail import send_mail
from django.shortcuts import render

from mvs.apps.email_form import form_to_email_html


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
        return [url(r"", self.view)]

    @staticmethod
    def view(request):
        form = ContactForm()
        if request.method == 'POST':
            form = ContactForm(request.POST)

            if form.is_valid():
                email_html = form_to_email_html(form)

                # Send to organization
                send_mail(
                    subject=form.cleaned_data['subject'],
                    message=email_html,
                    from_email=form.cleaned_data['email'],
                    recipient_list=["info@mezzeveulespeule.nl"],
                    fail_silently=True,
                    html_message=email_html,
                )

                # Send copy to volunteer
                send_mail(
                    subject=form.cleaned_data['subject'],
                    message=email_html,
                    from_email="info@mezzeveulespeule.nl",
                    recipient_list=[form.cleaned_data["email"]],
                    fail_silently=True,
                    html_message="<h1>Bedankt voor uw bericht</h1>"
                                 + "<p>We zullen er zo spoedig mogelijk op reageren!</p>"
                                 + email_html,
                )

                return render(request, "contact_thanks.html")

        return render(request, "contact.html", {"form": form})
