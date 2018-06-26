# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0374_importchangestatus_duplicate_attendees'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='role',
            field=app.models.UserRoles(max_length=20, default='vip', choices=[('student', 'Student'), ('participant', 'Participant'), ('speaker', 'Speaker'), ('vip', 'Vip')]),
        ),
    ]
