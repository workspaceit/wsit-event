# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0041_auto_20150902_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='room_order',
            field=models.IntegerField(max_length=10, default=1),
            preserve_default=False,
        ),
    ]
