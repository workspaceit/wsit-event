# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0204_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityhistory',
            name='activity_type',
            field=app.models.ActivityHistoryType(choices=[('update', 'Update'), ('register', 'Register'), ('message', 'Message'), ('offline', 'Offline Download')], max_length=50),
        ),
    ]
