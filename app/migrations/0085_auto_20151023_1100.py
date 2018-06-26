# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0084_group_is_searchable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='is_searchable',
            field=models.BooleanField(default=False),
        ),
    ]
