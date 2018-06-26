# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0355_presets_datetime_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentfilter',
            name='sorted_column',
            field=models.IntegerField(null=True, default=1),
        ),
        migrations.AddField(
            model_name='currentfilter',
            name='table_type',
            field=models.CharField(max_length=100, default='attendee'),
        ),
    ]
