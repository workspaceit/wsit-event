# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0273_attendeepasswordresetrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendee',
            name='push_notification_status',
            field=models.BooleanField(default=True),
        ),
    ]
