# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0126_auto_20160104_1123'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendee',
            name='event',
        ),
        migrations.RemoveField(
            model_name='questions',
            name='event',
        ),
        migrations.RemoveField(
            model_name='seminars',
            name='event',
        ),
        migrations.AddField(
            model_name='group',
            name='event',
            field=models.ForeignKey(default=1, to='app.Events'),
            preserve_default=False,
        ),
    ]
