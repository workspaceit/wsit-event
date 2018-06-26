# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0356_orders_is_preselected'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='is_preselected',
            field=models.BooleanField(default=False),
        ),
    ]
