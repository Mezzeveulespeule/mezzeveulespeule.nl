# Generated by Django 2.2.12 on 2020-04-05 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mvs', '0009_remove_old_plugins'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dag',
            options={'ordering': ('id',), 'verbose_name_plural': 'Dagen'},
        ),
        migrations.AddField(
            model_name='aanmelding',
            name='payment_id',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='aanmelding',
            name='allergien',
            field=models.TextField(blank=True),
        ),
    ]
