# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_hotel_room'),
    ]

    operations = [
        migrations.AddField(
            model_name='locations',
            name='description',
            field=models.TextField(default=None),
        ),
    ]
