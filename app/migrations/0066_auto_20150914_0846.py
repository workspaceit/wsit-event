# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0065_auto_20150912_1902'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='events',
            name='location',
        ),
        migrations.RemoveField(
            model_name='group',
            name='event',
        ),
        migrations.AlterField(
            model_name='locations',
            name='group',
            field=models.ForeignKey(to='app.Group'),
        ),
    ]
