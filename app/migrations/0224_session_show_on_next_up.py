# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0223_auto_20160827_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='show_on_next_up',
            field=models.BooleanField(default=True),
        ),
    ]
