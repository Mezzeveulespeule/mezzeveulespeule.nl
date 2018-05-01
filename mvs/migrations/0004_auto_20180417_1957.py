# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-17 17:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mvs', '0003_aanmelding_dag_taak_vrijwilliger'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='aanmelding',
            options={'verbose_name_plural': 'Aanmeldingen'},
        ),
        migrations.AlterModelOptions(
            name='dag',
            options={'verbose_name_plural': 'Dagen'},
        ),
        migrations.AlterModelOptions(
            name='taak',
            options={'verbose_name_plural': 'Taken'},
        ),
        migrations.AddField(
            model_name='aanmelding',
            name='opmerkingen',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='aanmelding',
            name='groepsmaatje',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='aanmelding',
            name='groepsmaatje_school',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='aanmelding',
            name='tel2',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='vrijwilliger',
            name='dagen',
            field=models.ManyToManyField(blank=True, to='mvs.Dag'),
        ),
        migrations.AlterField(
            model_name='vrijwilliger',
            name='eigen_kind',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='vrijwilliger',
            name='opmerkingen',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='vrijwilliger',
            name='taken',
            field=models.ManyToManyField(blank=True, to='mvs.Taak'),
        ),
        migrations.AlterField(
            model_name='vrijwilliger',
            name='tussenvoegsel',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
