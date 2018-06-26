# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0176_currentfilter'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentfilter',
            name='visible_columns',
            field=models.TextField(null=True, default=None),
        ),
        migrations.AlterField(
            model_name='currentfilter',
            name='filter',
            field=models.ForeignKey(null=True, default=None, to='app.RuleSet'),
        ),
    ]
