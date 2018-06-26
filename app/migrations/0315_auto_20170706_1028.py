# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0314_auto_20170706_1025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendee',
            name='type',
            field=app.models.AttendeeTypes(choices=[('user', 'User'), ('guest', 'Guest')], max_length=50, default='user'),
        ),
    ]
