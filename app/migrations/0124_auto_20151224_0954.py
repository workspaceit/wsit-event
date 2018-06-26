# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0123_auto_20151222_1244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityhistory',
            name='category',
            field=app.models.ActivityCategoryType(choices=[('event', 'Event'), ('session', 'Session'), ('question', 'Question'), ('travel', 'Travel'), ('room', 'Room'), ('message', 'Message'), ('profile', 'Profile')], max_length=50),
        ),
    ]
