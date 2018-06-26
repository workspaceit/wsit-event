# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0058_remove_booking_matched'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='broken_up',
            field=models.BooleanField(default=False),
        ),
    ]
