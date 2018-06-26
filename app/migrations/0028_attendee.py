# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_auto_20150826_1123'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('firstname', models.CharField(max_length=50)),
                ('lastname', models.CharField(max_length=45)),
                ('company', models.CharField(max_length=45)),
                ('email', models.CharField(max_length=45)),
                ('password', models.CharField(max_length=45)),
                ('phonenumber', models.CharField(max_length=45)),
                ('type', app.models.UserTypes(max_length=50, choices=[('super_admin', 'SuperAdmin'), ('admin', 'Admin'), ('user', 'User'), ('guest', 'Guest')], default='attendee')),
                ('status', app.models.AttendeeStatus(max_length=50, choices=[('canceled', 'Canceled'), ('registered', 'Registered'), ('pending', 'Pending')], default='registered')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('group', models.ForeignKey(to='app.Group')),
            ],
            options={
                'db_table': 'attendees',
            },
        ),
    ]
