# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0129_auto_20160105_1325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questions',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]
