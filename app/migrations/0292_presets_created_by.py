# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0291_auto_20170426_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='presets',
            name='created_by',
            field=models.ForeignKey(to='app.Users', default=1),
            preserve_default=False,
        ),
    ]
