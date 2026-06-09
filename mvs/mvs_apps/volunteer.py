from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django import forms
from django.conf.urls import url
from django.core.mail import send_mail, EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.shortcuts import render

from mvs.models import Vrijwilliger
from mvs.mvs_apps.email_form import form_to_email_html


class VolunteerForm(forms.ModelForm):
    title = "Vrijwilligers"

    class Meta:
        model = Vrijwilliger
        exclude = ['tussenvoegsel']  # Remove in DB remove once volunteers are cleared again

        labels = {
            "tel": "Telefoonnummer 1",
            "tel2": "Telefoonnummer 2",
            "ehbo": "Heb je een EHBO diploma?",
            "dagen": "Op welke dagen zou je (eventueel) kunnen komen helpen?",
            "taken": "Heb je een voorkeur voor een bepaalde taak?",
            "eigen_kind": "Indien je een groep wilt begeleiden, wil je jouw eigen kind in de groep? (Geef de naam van de kinderen die je in de groep wil:)",
            "opmerkingen": "Heb je nog andere opmerkingen?",
        }

        widgets = {
            "dagen": forms.CheckboxSelectMultiple,
            "taken": forms.CheckboxSelectMultiple,
            "geboortedatum": forms.DateInput(attrs={"type": "date"}),
        }


def process_volunteer_form(form: VolunteerForm):
    form.save()

    email_html = form_to_email_html(form)

    # Send to organization
    msg = EmailMultiAlternatives(
        subject="Nieuwe Vrijwilliger",
        body="Er is een nieuwe vrijwilliger aangemeld.",
        from_email="noreply@paulwagener.nl",
        reply_to=["info@mezzeveulespeule.nl"],
        to=["vrijwilligers@mezzeveulespeule.nl"],
    )
    msg.attach_alternative(email_html, "text/html")
    msg.send(fail_silently=True)

    # Send copy to volunteer
    volunteer_email = form.cleaned_data["email"]

    volunteer_html = (
        "<h1>Aanmelding Vrijwilliger</h1>"
        "<p>Bedankt voor je aanmelding!</p>"
        f"{email_html}"
    )

    msg = EmailMultiAlternatives(
        subject="Aanmelding Vrijwilliger",
        body="Bedankt voor je aanmelding!",
        from_email="noreply@paulwagener.nl",
        reply_to=["info@mezzeveulespeule.nl"],
        to=[volunteer_email],
    )
    msg.attach_alternative(volunteer_html, "text/html")
    msg.send(fail_silently=True)


@apphook_pool.register
class VolunteerHook(CMSApp):
    name = "Vrijwilligers"

    def get_urls(self, page=None, language=None, **kwargs):
        return [url(r"", self.view)]

    def view(self, request):
        # Show thank you message
        if "thanks" in request.session:
            del request.session["thanks"]
            return render(request, "volunteer_thanks.html")

        if request.method == "POST":
            # Validate form
            form = VolunteerForm(request.POST)

            if form.is_valid():
                process_volunteer_form(form)

                request.session["thanks"] = True
                return HttpResponseRedirect(request.path)
        else:
            form = VolunteerForm()

        # Show form
        return render(request, "volunteer.html", {"form": form})
