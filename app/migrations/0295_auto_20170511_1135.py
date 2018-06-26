# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0294_auto_20170502_1350'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityhistory',
            name='photo',
            field=models.ForeignKey(null=True, to='app.Photo'),
        ),
        migrations.AlterField(
            model_name='activityhistory',
            name='category',
            field=app.models.ActivityCategoryType(max_length=50, choices=[('event', 'Event'), ('session', 'Session'), ('question', 'Question'), ('travel', 'Travel'), ('room', 'Room'), ('message', 'Message'), ('profile', 'Profile'), ('push_notification', 'Push_notification'), ('group', 'Group'), ('tag', 'Tag'), ('package', 'Package'), ('checkpoint', 'Checkpoint'), ('photo', 'Photo')]),
        ),
        migrations.AlterField(
            model_name='deletedhistory',
            name='category',
            field=app.models.ActivityCategoryType(max_length=50, choices=[('event', 'Event'), ('session', 'Session'), ('question', 'Question'), ('travel', 'Travel'), ('room', 'Room'), ('message', 'Message'), ('profile', 'Profile'), ('push_notification', 'Push_notification'), ('group', 'Group'), ('tag', 'Tag'), ('package', 'Package'), ('checkpoint', 'Checkpoint'), ('photo', 'Photo')]),
        ),
    ]
