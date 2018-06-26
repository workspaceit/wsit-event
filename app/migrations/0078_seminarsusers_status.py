# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0077_attendee_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='seminarsusers',
            name='status',
            field=app.models.AttendeeSessionStatus(max_length=20, choices=[('attending', 'Attending'), ('in-queue', 'In Queue')], default='attending'),
        ),
    ]
