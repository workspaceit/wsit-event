# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0209_auto_20160601_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresetrequest',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 3, 17, 58, 49, 941467)),
        ),
        migrations.AlterField(
            model_name='session',
            name='max_attendees',
            field=models.IntegerField(null=True),
        ),
    ]
