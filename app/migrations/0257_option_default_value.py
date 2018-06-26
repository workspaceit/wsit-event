# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0256_auto_20161121_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='option',
            name='default_value',
            field=models.BooleanField(default=False),
        ),
    ]
