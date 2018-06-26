# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0313_auto_20170705_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendee',
            name='type',
            field=app.models.AttendeeTypes(choices=[('user', 'User'), ('guest', 'Guest'), ('temporary', 'Temporary')], default='user', max_length=50),
        ),
    ]
