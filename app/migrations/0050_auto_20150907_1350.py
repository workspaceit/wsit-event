# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0049_auto_20150903_1831'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roomallotment',
            name='room',
        ),
        migrations.DeleteModel(
            name='RoomAllotment',
        ),
    ]
