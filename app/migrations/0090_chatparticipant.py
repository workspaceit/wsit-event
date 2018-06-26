# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0089_auto_20151030_1616'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatParticipant',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('type', app.models.ChatTypes(max_length=100, choices=[('session', 'Session'), ('filter', 'Filter'), ('private', 'Private')])),
                ('attendee_id', models.ForeignKey(to='app.Attendee', null=True)),
                ('chat_room_id', models.ForeignKey(to='app.ChatRoom')),
                ('session_id', models.ForeignKey(to='app.Session', null=True)),
            ],
            options={
                'db_table': 'chat_participants',
            },
        ),
    ]
