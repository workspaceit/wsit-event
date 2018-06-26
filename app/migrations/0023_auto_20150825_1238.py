# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_auto_20150824_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='allow_attendees_queue',
            field=models.BooleanField(default=False),
        ),
    ]
