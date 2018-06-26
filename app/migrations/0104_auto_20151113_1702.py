# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0103_auto_20151113_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locations',
            name='description',
            field=models.TextField(default=None, null=True, blank=True),
        ),
    ]
