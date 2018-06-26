# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0074_auto_20150918_1657'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='has_time',
            field=models.BooleanField(default=True),
        ),
    ]
