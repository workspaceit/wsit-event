# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0214_auto_20160608_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresetrequest',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 14, 16, 41, 41, 298082)),
        ),
    ]
