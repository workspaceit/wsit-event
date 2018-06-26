# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0282_auto_20170403_1521'),
    ]

    operations = [
        migrations.AddField(
            model_name='seminarsusers',
            name='updated',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2017, 4, 3, 9, 23, 57, 634472, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='travelattendee',
            name='updated',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2017, 4, 3, 9, 24, 8, 362557, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='seminarsusers',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 4, 3, 9, 24, 35, 868774, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='travelattendee',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 4, 3, 9, 24, 52, 428482, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
