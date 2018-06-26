# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0062_group_is_show'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='group_order',
            field=models.IntegerField(default=1),
        ),
    ]
