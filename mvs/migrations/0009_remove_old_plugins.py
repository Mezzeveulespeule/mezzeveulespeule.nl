
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mvs', '0008_auto_20181011_1807'),
    ]

    operations = [
        migrations.RunSQL("DROP TABLE IF EXISTS cmsplugin_filer_file_filerfile"),
        migrations.RunSQL("DROP TABLE IF EXISTS cmsplugin_filer_folder_filerfolder"),
        migrations.RunSQL("DROP TABLE IF EXISTS cmsplugin_filer_image_filerimage"),
    ]
