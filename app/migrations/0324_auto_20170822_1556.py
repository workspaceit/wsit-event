# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0323_auto_20170821_1511'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rebates',
            name='item_type',
        ),
        migrations.AddField(
            model_name='rebates',
            name='type_id',
            field=models.TextField(default=None, null=True),
        ),
    ]
