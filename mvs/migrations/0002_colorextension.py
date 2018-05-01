# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-17 15:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
        ('mvs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ColorExtension',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=7)),
                ('extended_object', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='cms.Page')),
                ('public_extension', models.OneToOneField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='draft_extension', to='mvs.ColorExtension')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
