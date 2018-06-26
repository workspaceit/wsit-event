# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0281_auto_20170403_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 4, 3, 9, 20, 40, 443051, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='updated',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2017, 4, 3, 9, 20, 58, 307052, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hotel',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 4, 3, 9, 21, 8, 205062, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hotel',
            name='updated',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2017, 4, 3, 9, 21, 13, 147328, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='room',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 4, 3, 9, 21, 20, 139397, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='room',
            name='updated',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2017, 4, 3, 9, 21, 24, 876581, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='seminarspeakers',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 4, 3, 9, 21, 28, 563974, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='seminarspeakers',
            name='updated',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2017, 4, 3, 9, 21, 34, 410696, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='travel',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2017, 4, 3, 9, 21, 37, 842987, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='travel',
            name='updated',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2017, 4, 3, 9, 21, 44, 100176, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
