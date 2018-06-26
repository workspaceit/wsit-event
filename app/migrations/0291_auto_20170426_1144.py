# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0290_auto_20170421_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='presets',
            name='event',
            field=models.ForeignKey(null=True, to='app.Events'),
        ),
    ]
