# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_auto_20150821_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locations',
            name='latitude',
            field=models.CharField(max_length=50, default=None),
        ),
        migrations.AlterField(
            model_name='locations',
            name='longitude',
            field=models.CharField(max_length=50, default=None),
        ),
    ]
