# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0217_auto_20160621_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='all_dates',
            field=models.CharField(max_length=1000, default=None),
        ),
        migrations.AlterField(
            model_name='passwordresetrequest',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 20, 17, 47, 43, 40458)),
        ),
    ]
