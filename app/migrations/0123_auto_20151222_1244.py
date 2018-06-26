# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0122_auto_20151222_1207'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activityhistory',
            name='event_register',
        ),
        migrations.AlterField(
            model_name='activityhistory',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='activityhistory',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AlterField(
            model_name='messagehistory',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
