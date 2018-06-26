# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_auto_20150821_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locations',
            name='latitude',
            field=models.CharField(default=None, null=True, blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='locations',
            name='longitude',
            field=models.CharField(default=None, null=True, blank=True, max_length=50),
        ),
    ]
