# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0359_auto_20171215_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questions',
            name='from_date',
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='questions',
            name='from_time',
            field=models.TimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='questions',
            name='to_date',
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='questions',
            name='to_time',
            field=models.TimeField(blank=True, default=None, null=True),
        ),
    ]
