# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0105_auto_20151116_1750'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='show_on_evaluation',
            field=models.BooleanField(default=True),
        ),
    ]
