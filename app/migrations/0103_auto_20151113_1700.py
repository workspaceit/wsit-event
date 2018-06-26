# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0102_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locations',
            name='address',
            field=models.TextField(null=True, default=None, blank=True),
        ),
    ]
