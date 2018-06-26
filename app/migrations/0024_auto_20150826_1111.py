# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_auto_20150825_1238'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hotel',
            name='category',
        ),
        migrations.AddField(
            model_name='hotel',
            name='group',
            field=models.ForeignKey(to='app.Group', default=1),
            preserve_default=False,
        ),
    ]
