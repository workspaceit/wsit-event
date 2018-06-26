# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='event',
            field=models.ForeignKey(default=1, to='app.Events'),
            preserve_default=False,
        ),
    ]
