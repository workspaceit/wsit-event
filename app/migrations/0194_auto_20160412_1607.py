# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0193_auto_20160412_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='speakers',
            field=models.CharField(default=None, null=True, max_length=1024),
        ),
    ]
