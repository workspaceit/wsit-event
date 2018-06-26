# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0274_attendee_push_notification_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicetoken',
            name='offline_pakage_status',
            field=models.BooleanField(default=True),
        ),
    ]
