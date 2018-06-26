# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0042_room_room_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='total_rooms',
            field=models.IntegerField(default=4),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='room',
            name='room_order',
            field=models.IntegerField(),
        ),
    ]
