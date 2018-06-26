# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0284_auto_20170403_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 4, 4, 6, 23, 45, 984265, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='group',
            name='updated',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2017, 4, 4, 6, 24, 2, 831314, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='matchline',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 4, 4, 6, 24, 13, 335982, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='matchline',
            name='updated',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2017, 4, 4, 6, 24, 21, 23466, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='requestedbuddy',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 4, 4, 6, 24, 29, 32115, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='requestedbuddy',
            name='updated',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2017, 4, 4, 6, 24, 36, 743519, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
