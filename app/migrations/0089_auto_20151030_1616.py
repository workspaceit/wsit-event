# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0088_auto_20151030_1249'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatroom',
            name='attendee',
        ),
        migrations.RemoveField(
            model_name='chatroom',
            name='session',
        ),
        migrations.RemoveField(
            model_name='chatroom',
            name='type',
        ),
    ]
