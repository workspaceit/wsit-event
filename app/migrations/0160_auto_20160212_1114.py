# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0159_elements'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendee',
            name='type',
            field=app.models.AttendeeTypes(max_length=50, choices=[('user', 'User'), ('guest', 'Guest')], default='user'),
        ),
        migrations.AlterField(
            model_name='users',
            name='type',
            field=app.models.UserTypes(max_length=50, choices=[('super_admin', 'SuperAdmin'), ('admin', 'Admin'), ('third_party_admin', 'ThirdPartyAdmin')]),
        ),
    ]
