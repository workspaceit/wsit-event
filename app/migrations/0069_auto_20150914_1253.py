# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0068_auto_20150914_0935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questions',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='questions',
            name='type',
            field=models.CharField(max_length=255),
        ),
    ]
