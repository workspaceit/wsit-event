# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0327_auto_20170824_1642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitems',
            name='cost',
            field=models.FloatField(default=0),
        ),
    ]
