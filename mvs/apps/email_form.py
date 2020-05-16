import html

from django.db.models import QuerySet


def form_to_email_html(form):
    """
    Convert the input of a form for sending
    """
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

    return email_html
