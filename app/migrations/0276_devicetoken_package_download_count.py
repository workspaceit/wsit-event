# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0275_devicetoken_offline_pakage_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicetoken',
            name='package_download_count',
            field=models.IntegerField(default=0),
        ),
    ]
