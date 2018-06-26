# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0285_auto_20170404_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setting',
            name='value',
            field=models.CharField(max_length=500),
        ),
    ]
