# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0256_auto_20161121_1651'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedAttendee',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('firstname', models.CharField(max_length=50)),
                ('lastname', models.CharField(max_length=45)),
                ('email', models.CharField(max_length=45)),
                ('phonenumber', models.CharField(max_length=45)),
                ('deleted_at', models.DateTimeField(auto_now_add=True)),
                ('deleted_by', models.ForeignKey(to='app.Users')),
                ('event', models.ForeignKey(to='app.Events')),
            ],
            options={
                'db_table': 'deleted_attendees',
            },
        ),
        migrations.CreateModel(
            name='DeletedHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('activity_type', app.models.ActivityHistoryType(choices=[('update', 'Update'), ('register', 'Register'), ('message', 'Message'), ('offline', 'Offline Download')], max_length=50)),
                ('category', app.models.ActivityCategoryType(choices=[('event', 'Event'), ('session', 'Session'), ('question', 'Question'), ('travel', 'Travel'), ('room', 'Room'), ('message', 'Message'), ('profile', 'Profile'), ('push_notification', 'Push_notification'), ('group', 'Group'), ('tag', 'Tag')], max_length=50)),
                ('old_value', models.TextField()),
                ('new_value', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('admin', models.ForeignKey(to='app.Users', null=True)),
                ('attendee', models.ForeignKey(to='app.DeletedAttendee')),
                ('event', models.ForeignKey(to='app.Events')),
                ('message', models.ForeignKey(to='app.MessageHistory', null=True)),
                ('question', models.ForeignKey(to='app.Questions', null=True)),
                ('room', models.ForeignKey(to='app.Room', null=True)),
                ('session', models.ForeignKey(to='app.Session', null=True)),
                ('travel', models.ForeignKey(to='app.Travel', null=True)),
            ],
            options={
                'db_table': 'deleted_history',
            },
        ),
    ]
