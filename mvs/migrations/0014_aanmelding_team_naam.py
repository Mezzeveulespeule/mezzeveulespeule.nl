# Generated by Django 2.2.12 on 2020-05-21 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mvs', '0013_auto_20200517_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='aanmelding',
            name='team_naam',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
