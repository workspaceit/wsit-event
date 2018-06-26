# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0131_eventadmin'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminPermission',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('access_level', app.models.AccessLevel(max_length=10, choices=[('read', 'Read'), ('write', 'Write'), ('none', 'None')], default='none')),
                ('description', models.CharField(max_length=100, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('admin', models.ForeignKey(to='app.Users')),
                ('group', models.ForeignKey(to='app.Group')),
            ],
            options={
                'db_table': 'admin_permissions',
            },
        ),
    ]
