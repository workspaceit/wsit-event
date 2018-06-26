# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20150819_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locations',
            name='event',
            field=models.ForeignKey(blank=True, to='app.Events'),
        ),
    ]
