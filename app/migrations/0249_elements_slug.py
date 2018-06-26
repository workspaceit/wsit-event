# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0248_auto_20161102_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='elements',
            name='slug',
            field=models.CharField(max_length=255, default=''),
        ),
    ]
