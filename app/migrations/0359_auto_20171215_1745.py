# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0358_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='from_date',
            field=models.DateField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='questions',
            name='from_time',
            field=models.TimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='questions',
            name='to_date',
            field=models.DateField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='questions',
            name='to_time',
            field=models.TimeField(default=None, null=True),
        ),
    ]
