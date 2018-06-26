# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0246_auto_20161031_1346'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailReceivers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('firstname', models.CharField(max_length=255)),
                ('lastname', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('status', app.models.ReceiversStatus(max_length=100, default='not_sent', choices=[('sent', 'Sent'), ('not_sent', 'Not_sent')])),
                ('last_received', models.DateTimeField(auto_now=True)),
                ('is_show', models.BooleanField(default=True)),
                ('added_by', models.ForeignKey(to='app.Users')),
                ('attendee', models.ForeignKey(null=True, to='app.Attendee')),
                ('email_content', models.ForeignKey(to='app.EmailContents')),
            ],
            options={
                'db_table': 'email_receivers',
            },
        ),
        migrations.CreateModel(
            name='EmailReceiversHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('sending_at', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(to='app.EmailReceivers')),
            ],
            options={
                'db_table': 'email_receivers_history',
            },
        ),
        migrations.CreateModel(
            name='MessageContents',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('sender_name', models.CharField(max_length=255)),
                ('type', app.models.MessageType(max_length=255, choices=[('push_or_sms', 'Push_or_Sms'), ('sms_and_push', 'Sms_and_Push'), ('sms', 'Sms'), ('push', 'Push')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_show', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(to='app.Users', related_name='message_created_by')),
                ('last_updated_by', models.ForeignKey(to='app.Users', related_name='message_last_updated_by')),
            ],
            options={
                'db_table': 'message_contents',
            },
        ),
        migrations.CreateModel(
            name='MessageReceivers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('firstname', models.CharField(max_length=255)),
                ('lastname', models.CharField(max_length=255)),
                ('mobile_phone', models.CharField(max_length=255)),
                ('status', app.models.ReceiversStatus(max_length=100, default='not_sent', choices=[('sent', 'Sent'), ('not_sent', 'Not_sent')])),
                ('last_received', models.DateTimeField(auto_now=True)),
                ('is_show', models.BooleanField(default=True)),
                ('added_by', models.ForeignKey(to='app.Users')),
                ('attendee', models.ForeignKey(null=True, to='app.Attendee')),
                ('message_content', models.ForeignKey(to='app.MessageContents')),
            ],
            options={
                'db_table': 'message_receivers',
            },
        ),
        migrations.CreateModel(
            name='MessageReceiversHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('type', app.models.MessageHistoryType(max_length=100, choices=[('sms', 'SMS'), ('push', 'PUSH')])),
                ('sending_at', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(to='app.EmailReceivers')),
            ],
            options={
                'db_table': 'message_receivers_history',
            },
        ),
    ]
