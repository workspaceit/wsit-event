# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0237_remove_menupermission_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='menupermission',
            name='allow_unregistered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='menupermission',
            name='rule',
            field=models.ForeignKey(default=None, null=True, to='app.RuleSet'),
        ),
    ]
