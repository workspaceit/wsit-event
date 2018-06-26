# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0079_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='clash_session',
            field=models.ForeignKey(to='app.Session', null=True, related_name='notification_clash_session'),
        ),
        migrations.AddField(
            model_name='notification',
            name='new_session',
            field=models.ForeignKey(to='app.Session', null=True, related_name='notification_new_session'),
        ),
        migrations.AddField(
            model_name='notification',
            name='sender_attendee',
            field=models.ForeignKey(to='app.Attendee', null=True, related_name='notification_sender_attendee'),
        ),
        migrations.AddField(
            model_name='notification',
            name='status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='notification',
            name='to_attendee',
            field=models.ForeignKey(to='app.Attendee', related_name='notification_to_attendee'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=app.models.NotificationTypes(max_length=100, choices=[('session', 'Session'), ('admin', 'Admin'), ('attendee', 'Attendee'), ('group', 'Group')]),
        ),
    ]
