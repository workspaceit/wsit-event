# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0356_auto_20171206_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentfilter',
            name='sorting_order',
            field=models.CharField(max_length=32, default='asc'),
        ),
    ]
