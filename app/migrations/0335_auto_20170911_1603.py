# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0334_auto_20170911_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='cost',
            field=models.FloatField(default=0),
        ),
    ]
