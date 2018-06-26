# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_auto_20150826_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='vat',
            field=models.DecimalField(max_digits=8, decimal_places=2),
        ),
    ]
