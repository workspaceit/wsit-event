# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0078_seminarsusers_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', app.models.NotificationTypes(max_length=20, choices=[('session', 'Session'), ('admin', 'Admin'), ('attendee', 'Attendee'), ('group', 'Group')])),
                ('message', models.TextField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('to_attendee', models.ForeignKey(to='app.Attendee')),
            ],
            options={
                'db_table': 'notifications',
            },
        ),
    ]
