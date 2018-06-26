# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_auto_20150819_1512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locations',
            name='contacts',
            field=models.TextField(blank=True, default=None),
        ),
        migrations.AlterField(
            model_name='locations',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
    ]
