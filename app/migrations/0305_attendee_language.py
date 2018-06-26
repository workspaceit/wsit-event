# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0304_auto_20170523_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendee',
            name='language',
            field=models.ForeignKey(default=7, to='app.Presets'),
            preserve_default=False,
        ),
    ]
