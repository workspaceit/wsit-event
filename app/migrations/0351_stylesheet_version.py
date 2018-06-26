# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0350_auto_20171011_1237'),
    ]

    operations = [
        migrations.AddField(
            model_name='stylesheet',
            name='version',
            field=models.IntegerField(default=1),
        ),
    ]
