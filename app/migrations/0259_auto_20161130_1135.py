# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0258_auto_20161128_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityhistory',
            name='activity_type',
            field=app.models.ActivityHistoryType(choices=[('update', 'Update'), ('delete', 'Delete'), ('register', 'Register'), ('message', 'Message'), ('offline', 'Offline Download')], max_length=50),
        ),
        migrations.AlterField(
            model_name='deletedhistory',
            name='activity_type',
            field=app.models.ActivityHistoryType(choices=[('update', 'Update'), ('delete', 'Delete'), ('register', 'Register'), ('message', 'Message'), ('offline', 'Offline Download')], max_length=50),
        ),
    ]
