# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0060_usedrule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usedrule',
            name='rule',
            field=models.ForeignKey(to='app.RuleSet', related_name='rules'),
        ),
        migrations.AlterField(
            model_name='usedrule',
            name='user',
            field=models.ForeignKey(to='app.Users'),
        ),
    ]
