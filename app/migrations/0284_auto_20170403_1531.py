# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0283_auto_20170403_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicetoken',
            name='package_created_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='devicetoken',
            name='package_version',
            field=models.IntegerField(default=0),
        ),
    ]
