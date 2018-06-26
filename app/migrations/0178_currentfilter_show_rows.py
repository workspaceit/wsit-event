# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0177_auto_20160315_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentfilter',
            name='show_rows',
            field=models.IntegerField(default=None, null=True),
        ),
    ]
