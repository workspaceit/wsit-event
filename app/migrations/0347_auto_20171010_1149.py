# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0346_auto_20171005_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='presets',
            name='date_format',
            field=models.CharField(default='Y-m-d', max_length=50),
        ),
        migrations.AddField(
            model_name='presets',
            name='datetime_format',
            field=models.CharField(default='Y-m-d H:i', max_length=50),
        ),
        migrations.AddField(
            model_name='presets',
            name='language_code',
            field=models.CharField(default='en', max_length=10),
        ),
        migrations.AddField(
            model_name='presets',
            name='time_format',
            field=models.CharField(default='H:i', max_length=50),
        ),
    ]
