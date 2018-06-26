# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0320_auto_20170801_1326'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='cost',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='session',
            name='vat',
            field=models.FloatField(null=True),
        ),
    ]
