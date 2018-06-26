# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0039_attendeerooms'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roomattendee',
            name='attendee',
        ),
        migrations.RemoveField(
            model_name='roomattendee',
            name='booking',
        ),
        migrations.DeleteModel(
            name='RoomAttendee',
        ),
    ]
