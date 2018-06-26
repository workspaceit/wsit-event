# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0238_auto_20160928_1650'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menupermission',
            name='allow_unregistered',
        ),
        migrations.AddField(
            model_name='menuitem',
            name='allow_unregistered',
            field=models.BooleanField(default=False),
        ),
    ]
