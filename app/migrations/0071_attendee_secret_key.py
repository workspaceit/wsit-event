# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0070_auto_20150914_1258'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendee',
            name='secret_key',
            field=models.CharField(max_length=50, default=1),
            preserve_default=False,
        ),
    ]
