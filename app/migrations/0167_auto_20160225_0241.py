# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0166_devicetoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicetoken',
            name='is_enable',
            field=models.BooleanField(default=True),
        ),
    ]
