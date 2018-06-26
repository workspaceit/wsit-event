# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0208_passwordresetrequest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='passwordresetrequest',
            name='attendee',
        ),
        migrations.AddField(
            model_name='passwordresetrequest',
            name='user',
            field=models.ForeignKey(default=None, to='app.Users'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='passwordresetrequest',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 2, 15, 40, 2, 580224)),
        ),
    ]
