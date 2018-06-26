# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0280_auto_20170324_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 4, 3, 9, 14, 22, 1971, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='session',
            name='updated',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2017, 4, 3, 9, 14, 30, 874162, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
