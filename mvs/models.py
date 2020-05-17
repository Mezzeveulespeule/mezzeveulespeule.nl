from cms.extensions import PageExtension
from cms.extensions.extension_pool import extension_pool
from django.db import models


class ColorExtension(PageExtension):
    color = models.CharField(max_length=7)


extension_pool.register(ColorExtension)


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

    geslacht = models.CharField(max_length=10, choices=(("M", "Man"), ("V", "Vrouw"),))

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
    achternaam = models.CharField(max_length=100)

    adres = models.CharField(max_length=500)
    postcode = models.CharField(max_length=7)
    woonplaats = models.CharField(max_length=100)

    email = models.EmailField()
    tel = models.CharField(max_length=100)
    tel2 = models.CharField(max_length=100, blank=True)

    opmerkingen = models.TextField(blank=True)

    inschrijf_datum = models.DateTimeField(auto_now_add=True)

    kinderen = models.IntegerField(choices=[(i, i) for i in range(1, 6)])

    kind1_naam = models.CharField(max_length=100)
    kind1_leeftijd = models.IntegerField()

    kind2_naam = models.CharField(max_length=100, blank=True)
    kind2_leeftijd = models.IntegerField(blank=True, null=True)

    kind3_naam = models.CharField(max_length=100, blank=True)
    kind3_leeftijd = models.IntegerField(blank=True, null=True)

    kind4_naam = models.CharField(max_length=100, blank=True)
    kind4_leeftijd = models.IntegerField(blank=True, null=True)

    kind5_naam = models.CharField(max_length=100, blank=True)
    kind5_leeftijd = models.IntegerField(blank=True, null=True)

    kind6_naam = models.CharField(max_length=100, blank=True)
    kind6_leeftijd = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "{0} {1} ({2})".format(
            self.voornaam, self.achternaam, self.inschrijf_datum.strftime("%c")
        )

    class Meta:
        verbose_name_plural = "Aanmeldingen"
        ordering = ["-inschrijf_datum"]
