# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0061_auto_20150911_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='is_show',
            field=models.BooleanField(default=True),
        ),
    ]
