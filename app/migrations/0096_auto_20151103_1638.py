# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0095_auto_20151102_1801'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=app.models.NotificationTypes(max_length=100, choices=[('session', 'Session'), ('admin', 'Admin'), ('attendee', 'Attendee'), ('group', 'Group'), ('session_attend', 'Session_attend')]),
        ),
    ]
