# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0125_auto_20160104_1120'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='description',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='events',
            name='end',
            field=models.DateField(default=datetime.datetime(2016, 1, 4, 5, 23, 43, 281982, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='events',
            name='start',
            field=models.DateField(default=datetime.datetime(2016, 1, 4, 5, 23, 53, 322023, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
