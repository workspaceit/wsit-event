# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0104_auto_20151113_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=app.models.NotificationTypes(choices=[('session', 'Session'), ('admin', 'Admin'), ('attendee', 'Attendee'), ('group', 'Group'), ('session_attend', 'Session_attend'), ('session_broadcast', 'Session_broadcast')], max_length=100),
        ),
    ]
