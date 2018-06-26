# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0124_auto_20151224_0954'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='events',
            name='date',
        ),
        migrations.RemoveField(
            model_name='events',
            name='location',
        ),
    ]
