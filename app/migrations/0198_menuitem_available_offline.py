# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0197_auto_20160419_1136'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='available_offline',
            field=models.BooleanField(default=False),
        ),
    ]
