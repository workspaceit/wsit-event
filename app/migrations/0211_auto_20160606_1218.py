# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0210_auto_20160602_1758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresetrequest',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 7, 12, 18, 33, 996211)),
        ),
        migrations.AlterField(
            model_name='session',
            name='max_attendees',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
