from django.db import models


class Dag(models.Model):
    naam = models.CharField(max_length=100)

    def __str__(self):
        return self.naam

    class Meta:
        verbose_name_plural = "Dagen"
        ordering = ("id",)


class Taak(models.Model):
    naam = models.CharField(max_length=100)

    def __str__(self):
        return self.naam

    class Meta:
        verbose_name_plural = "Taken"


class Vrijwilliger(models.Model):
    voornaam = models.CharField(max_length=100)
    tussenvoegsel = models.CharField(max_length=50, blank=True)
    achternaam = models.CharField(max_length=100)

    geslacht = models.CharField(
        max_length=10,
        choices=(
            ("M", "Man"),
            ("V", "Vrouw"),
        ),
    )

    adres = models.CharField(max_length=100)
    postcode = models.CharField(max_length=7)
    woonplaats = models.CharField(max_length=100)

    email = models.EmailField()

    ehbo = models.BooleanField()

    geboortedatum = models.DateField()
    tel = models.CharField(max_length=50)
    tel2 = models.CharField(max_length=50, blank=True)
    stage = models.BooleanField()

    dagen = models.ManyToManyField(Dag, blank=True)
    taken = models.ManyToManyField(Taak, blank=True)

    eigen_kind = models.CharField(max_length=100, blank=True)
    opmerkingen = models.TextField(blank=True)

    aanmelding_timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{0} {1} {2}".format(self.voornaam, self.tussenvoegsel, self.achternaam)


scholen = [
    ("De Sleutelaar", "De Sleutelaar"),
    ("De Toermalijn", "De Toermalijn"),
    ("Franciscusschool", "Franciscusschool"),
    ("Mariaschool", "Mariaschool"),
    ("De Piramide", "De Piramide"),
]


class Aanmelding(models.Model):
    voornaam = models.CharField(max_length=100)
    achternaam = models.CharField(max_length=100)
    geslacht = models.CharField(
        max_length=1, default=None, choices=[("M", "Jongen"), ("F", "Meisje")]
    )
    klas = models.CharField(
        max_length=1,
        choices=[
            ("1", "Groep 1"),
            ("2", "Groep 2"),
            ("3", "Groep 3"),
            ("4", "Groep 4"),
            ("5", "Groep 5"),
            ("6", "Groep 6"),
            ("7", "Groep 7"),
            ("8", "Groep 8"),
        ],
    )
    adres = models.CharField(max_length=500)
    postcode = models.CharField(max_length=7)
    woonplaats = models.CharField(max_length=100)

    email = models.EmailField()
    tel1 = models.CharField(max_length=100)
    tel2 = models.CharField(max_length=100, blank=True)
    school = models.CharField(max_length=100, default=None)

    allergien = models.TextField()

    groepsmaatje = models.CharField(max_length=100, blank=True)
    groepsmaatje_school = models.CharField(max_length=100, blank=True)

    overnachting = models.BooleanField(default=False)

    opmerkingen = models.TextField(blank=True)

    inschrijf_datum = models.DateTimeField(auto_now_add=True)
    organisatie = models.BooleanField(default=False)

    def __str__(self):
        return "{0} {1} ({2})".format(
            self.voornaam, self.achternaam, self.inschrijf_datum.strftime("%c")
        )

    class Meta:
        verbose_name_plural = "Aanmeldingen"
        ordering = ["-inschrijf_datum"]
