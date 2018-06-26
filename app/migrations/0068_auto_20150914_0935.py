# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0067_events_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questions',
            name='group',
            field=models.ForeignKey(to='app.Group'),
        ),
    ]
