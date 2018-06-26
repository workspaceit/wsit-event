# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0349_auto_20171011_1152'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payments',
            name='order',
        ),
        migrations.AddField(
            model_name='payments',
            name='order_number',
            field=models.IntegerField(default=0),
        ),
    ]
