# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0164_auto_20160215_1727'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='all_day',
            field=models.BooleanField(default=False),
        ),
    ]
