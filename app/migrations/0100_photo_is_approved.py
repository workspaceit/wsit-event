# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0099_scan'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='is_approved',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
