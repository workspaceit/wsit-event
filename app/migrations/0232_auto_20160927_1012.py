# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0231_presets_created_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='elementdefaultlang',
            old_name='value',
            new_name='default_value',
        ),
        migrations.AlterField(
            model_name='elementdefaultlang',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
