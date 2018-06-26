# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0216_auto_20160613_1643'),
    ]

    operations = [
        migrations.AddField(
            model_name='option',
            name='option_order',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='passwordresetrequest',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 22, 15, 16, 27, 315287)),
        ),
    ]
