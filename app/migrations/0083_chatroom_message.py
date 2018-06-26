# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0082_setting'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('type', app.models.ChatTypes(choices=[('session', 'Session'), ('filter', 'Filter'), ('attendee', 'Attendee')], max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('attendee', models.ForeignKey(null=True, to='app.Attendee')),
                ('session', models.ForeignKey(null=True, to='app.Session')),
            ],
            options={
                'db_table': 'chat_rooms',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('text', models.TextField(default=None)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('chat_room', models.ForeignKey(to='app.ChatRoom')),
                ('sender', models.ForeignKey(to='app.Attendee')),
            ],
            options={
                'db_table': 'messages',
            },
        ),
    ]
