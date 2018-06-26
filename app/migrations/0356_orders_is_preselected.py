# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0355_presets_datetime_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='is_preselected',
            field=models.IntegerField(default=0),
        ),
    ]
