# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0219_auto_20160721_1234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elementsanswers',
            name='answer',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='passwordresetrequest',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 26, 17, 27, 7, 592916)),
        ),
    ]
