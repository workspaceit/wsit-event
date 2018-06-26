# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0044_auto_20150903_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='group_order',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
