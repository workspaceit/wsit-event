# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0048_auto_20150903_1827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestedbuddy',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
