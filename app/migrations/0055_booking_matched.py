# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0054_match_matchline'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='matched',
            field=models.BooleanField(default=False),
        ),
    ]
