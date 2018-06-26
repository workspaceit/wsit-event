# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0109_auto_20151126_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locations',
            name='name',
            field=models.CharField(unique=True, max_length=45),
        ),
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=app.models.NotificationTypes(choices=[('session', 'Session'), ('admin', 'Admin'), ('attendee', 'Attendee'), ('group', 'Group'), ('session_attend', 'Session_attend'), ('filter_message', 'Filter_message')], max_length=100),
        ),
        migrations.AlterField(
            model_name='questions',
            name='title',
            field=models.CharField(unique=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='session',
            name='name',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]
