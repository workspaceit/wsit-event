# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0337_auto_20170913_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitems',
            name='rebate_amount',
            field=models.FloatField(default=0),
        ),
    ]
