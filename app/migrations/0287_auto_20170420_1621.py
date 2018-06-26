# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0286_auto_20170418_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityhistory',
            name='activity_type',
            field=app.models.ActivityHistoryType(choices=[('update', 'Update'), ('delete', 'Delete'), ('register', 'Register'), ('message', 'Message'), ('offline', 'Offline Download'), ('check-in', 'Check In')], max_length=50),
        ),
        migrations.AlterField(
            model_name='activityhistory',
            name='category',
            field=app.models.ActivityCategoryType(choices=[('event', 'Event'), ('session', 'Session'), ('question', 'Question'), ('travel', 'Travel'), ('room', 'Room'), ('message', 'Message'), ('profile', 'Profile'), ('push_notification', 'Push_notification'), ('group', 'Group'), ('tag', 'Tag'), ('package', 'Package'), ('checkpoint', 'Checkpoint')], max_length=50),
        ),
        migrations.AlterField(
            model_name='deletedhistory',
            name='activity_type',
            field=app.models.ActivityHistoryType(choices=[('update', 'Update'), ('delete', 'Delete'), ('register', 'Register'), ('message', 'Message'), ('offline', 'Offline Download'), ('check-in', 'Check In')], max_length=50),
        ),
        migrations.AlterField(
            model_name='deletedhistory',
            name='category',
            field=app.models.ActivityCategoryType(choices=[('event', 'Event'), ('session', 'Session'), ('question', 'Question'), ('travel', 'Travel'), ('room', 'Room'), ('message', 'Message'), ('profile', 'Profile'), ('push_notification', 'Push_notification'), ('group', 'Group'), ('tag', 'Tag'), ('package', 'Package'), ('checkpoint', 'Checkpoint')], max_length=50),
        ),
    ]
