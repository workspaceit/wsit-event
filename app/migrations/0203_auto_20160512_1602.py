# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0202_auto_20160512_1512'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendeemessage',
            name='attendee',
        ),
        migrations.RemoveField(
            model_name='attendeemessage',
            name='message',
        ),
        migrations.DeleteModel(
            name='AttendeeMessage',
        ),
    ]
