# Generated by Django 2.2.12 on 2020-05-21 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mvs', '0014_aanmelding_team_naam'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aanmelding',
            name='woonplaats',
            field=models.CharField(default='Bladel', max_length=100),
        ),
    ]
