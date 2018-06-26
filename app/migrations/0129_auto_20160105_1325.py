# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0128_users_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='status',
            field=app.models.UserStatus(max_length=20, default='active', choices=[('active', 'Active'), ('inactive', 'Inactive')]),
        ),
    ]
