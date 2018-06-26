# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0331_auto_20170829_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rebates',
            name='value',
            field=models.FloatField(),
        ),
    ]
