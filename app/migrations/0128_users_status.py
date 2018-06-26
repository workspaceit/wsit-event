# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0127_auto_20160104_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='status',
            field=app.models.UserStatus(choices=[('active', 'Active'), ('inactive', 'Inactive')], max_length=20, default='active'),
            preserve_default=False,
        ),
    ]
