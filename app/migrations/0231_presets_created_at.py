# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0230_elementdefaultlang_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='presets',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 9, 27, 4, 9, 45, 956991, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
