import html

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django import forms
from django.conf.urls import url
from django.core.mail import send_mail
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import render

from mvs.models import Vrijwilliger


class VrijwilligerForm(forms.ModelForm):
    title = "Vrijwilligers"

    class Meta:
        model = Vrijwilliger
        exclude = ['tussenvoegsel']  # Remove in DB remove once volunteers are cleared again

        labels = {
            "tel": "Telefoonnummer 1",
            "tel2": "Telefoonnummer 2",
            "ehbo": "Heb je een EHBO diploma?",
            "stage": "Ben je vrijwilliger voor een maatschappelijke stage?",
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


def process_volunteer_form(form: VrijwilligerForm):
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
            data = "Ja" if data else "Nee"

        elif isinstance(data, QuerySet):
            data = ", ".join(map(str, data))
        else:
            data = str(data)

        email_html += (
                "<tr><th>" + field.label + ":</th><td>" + html.escape(data) + "<td></tr>"
        )

    email_html += "</table>"

    # Send to organization
    send_mail(
        "Nieuwe Vrijwilliger",
        email_html,
        "info@mezzeveulespeule.nl",
        ["vrijwilligers@mezzeveulespeule.nl"],
        fail_silently=True,
        html_message=email_html,
    )

    # Send copy to volunteer
    volunteer_email = form.cleaned_data["email"]
    send_mail(
        "Aanmelding Vrijwilliger",
        "Bedankt voor je aanmelding!",
        "info@mezzeveulespeule.nl",
        [volunteer_email],
        fail_silently=True,
        html_message="<h1>Aanmelding Vrijwillliger</h1>"
                     + "<p>Bedankt voor je aanmelding!</p>"
                     + email_html,
    )


@apphook_pool.register
class VolunteerHook(CMSApp):
    name = "Vrijwilligers"

    def get_urls(self, page=None, language=None, **kwargs):
        return [url(r"", self.view)]

    def view(self, request):
        # Show thank you message
        if "thanks" in request.session:
            del request.session["thanks"]
            return render(request, "vrijwilliger_thanks.html")

        if request.method == "POST":
            # Validate form
            form = VrijwilligerForm(request.POST)

            if form.is_valid():
                process_volunteer_form(form)

                request.session["thanks"] = True
                return HttpResponseRedirect(request.path)
        else:
            form = VrijwilligerForm()

        # Show form
        return render(request, "vrijwilliger.html", {"form": form})
