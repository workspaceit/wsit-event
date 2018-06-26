# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0133_contentpermission'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupPermission',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('access_level', app.models.AccessLevel(choices=[('read', 'Read'), ('write', 'Write'), ('none', 'None')], default='none', max_length=10)),
                ('description', models.CharField(null=True, max_length=100)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('admin', models.ForeignKey(to='app.Users')),
                ('group', models.ForeignKey(to='app.Group')),
            ],
            options={
                'db_table': 'group_permissions',
            },
        ),
        migrations.RemoveField(
            model_name='adminpermission',
            name='admin',
        ),
        migrations.RemoveField(
            model_name='adminpermission',
            name='group',
        ),
        migrations.DeleteModel(
            name='AdminPermission',
        ),
    ]
