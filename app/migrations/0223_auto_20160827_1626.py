# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0222_auto_20160802_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='ruleset',
            name='is_limit',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ruleset',
            name='limit_amount',
            field=models.IntegerField(default=0),
        ),
    ]
