# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0333_auto_20170909_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='rebate_amount',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='orders',
            name='vat_amount',
            field=models.FloatField(default=0),
        ),
    ]
