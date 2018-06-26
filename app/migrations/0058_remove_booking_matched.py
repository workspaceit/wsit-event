# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0057_auto_20150909_1428'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='matched',
        ),
    ]
