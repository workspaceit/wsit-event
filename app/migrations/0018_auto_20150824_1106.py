# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_auto_20150821_1139'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='locations',
            name='event',
        ),
        migrations.AddField(
            model_name='events',
            name='location',
            field=models.ForeignKey(default=1, to='app.Locations'),
            preserve_default=False,
        ),
    ]
