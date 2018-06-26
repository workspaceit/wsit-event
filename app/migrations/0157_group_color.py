# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0156_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='color',
            field=models.CharField(default=None, max_length=20),
        ),
    ]
