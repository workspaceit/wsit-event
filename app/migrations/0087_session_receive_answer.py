# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0086_auto_20151026_1436'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='receive_answer',
            field=models.BooleanField(default=False),
        ),
    ]
