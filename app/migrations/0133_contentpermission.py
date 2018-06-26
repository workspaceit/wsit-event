# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0132_adminpermission'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', app.models.ContentType(choices=[('event', 'Event'), ('session', 'Session'), ('question', 'Question'), ('travel', 'Travel'), ('location', 'Location'), ('hotel', 'Hotel'), ('filter', 'Filter'), ('export_filter', 'ExportFilter'), ('photo_reel', 'PhotoReel'), ('message', 'Message'), ('setting', 'Setting'), ('assign_session', 'AssignSession'), ('assign_travel', 'AssignTravel'), ('assign_hotel', 'AssignHotel')], max_length=20)),
                ('access_level', app.models.AccessLevel(choices=[('read', 'Read'), ('write', 'Write'), ('none', 'None')], max_length=10, default='none')),
                ('description', models.CharField(null=True, max_length=100)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('admin', models.ForeignKey(to='app.Users')),
            ],
            options={
                'db_table': 'content_permissions',
            },
        ),
    ]
