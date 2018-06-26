# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0215_auto_20160613_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendee',
            name='password',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='passwordresetrequest',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 14, 16, 42, 59, 895686)),
        ),
    ]
