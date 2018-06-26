# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0375_auto_20180430_1847'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='time_interval',
            field=models.CharField(null=True, max_length=2),
        ),
    ]
