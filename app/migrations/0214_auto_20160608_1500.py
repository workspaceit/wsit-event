# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0213_auto_20160607_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresetrequest',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 9, 15, 0, 31, 95328)),
        ),
        migrations.AlterModelTable(
            name='checkpoint',
            table='checkpoints',
        ),
    ]
