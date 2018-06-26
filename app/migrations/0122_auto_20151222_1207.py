# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0121_auto_20151215_1052'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('activity_type', app.models.ActivityHistoryType(choices=[('update', 'Update'), ('register', 'Register'), ('message', 'Message')], max_length=50)),
                ('category', app.models.ActivityCategoryType(choices=[('event', 'Event'), ('session', 'Session'), ('question', 'Question'), ('travel', 'Travel'), ('room', 'Room'), ('message', 'Message')], max_length=50)),
                ('old_value', models.TextField()),
                ('new_value', models.TextField()),
                ('created', models.DateField(auto_now_add=True)),
                ('admin', models.ForeignKey(null=True, to='app.Users')),
                ('attendee', models.ForeignKey(to='app.Attendee')),
                ('event', models.ForeignKey(to='app.Events', related_name='history_event')),
                ('event_register', models.ForeignKey(related_name='history_register_event', to='app.Events', null=True)),
            ],
            options={
                'db_table': 'activity_history',
            },
        ),
        migrations.CreateModel(
            name='MessageHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('subject', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('type', app.models.MessageHistoryType(choices=[('message', 'Message'), ('sms', 'SMS'), ('mail', 'Mail')], max_length=50)),
                ('created', models.DateField(auto_now_add=True)),
                ('admin', models.ForeignKey(to='app.Users')),
                ('attendee', models.ForeignKey(to='app.Attendee')),
            ],
            options={
                'db_table': 'message_history',
            },
        ),
        migrations.AddField(
            model_name='activityhistory',
            name='message',
            field=models.ForeignKey(null=True, to='app.MessageHistory'),
        ),
        migrations.AddField(
            model_name='activityhistory',
            name='question',
            field=models.ForeignKey(null=True, to='app.Questions'),
        ),
        migrations.AddField(
            model_name='activityhistory',
            name='room',
            field=models.ForeignKey(null=True, to='app.Room'),
        ),
        migrations.AddField(
            model_name='activityhistory',
            name='session',
            field=models.ForeignKey(null=True, to='app.Session'),
        ),
        migrations.AddField(
            model_name='activityhistory',
            name='travel',
            field=models.ForeignKey(null=True, to='app.Travel'),
        ),
    ]
