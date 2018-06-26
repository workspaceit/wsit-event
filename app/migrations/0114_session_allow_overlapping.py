# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0113_auto_20151130_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='allow_overlapping',
            field=models.BooleanField(default=False),
        ),
    ]
