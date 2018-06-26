# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0165_session_all_day'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceToken',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('device_unique_id', models.CharField(max_length=255)),
                ('token', models.CharField(max_length=255)),
                ('os_type', app.models.OsType(choices=[('1', 'Android'), ('2', 'IOS')])),
                ('arn_enpoint', models.CharField(max_length=255)),
                ('is_enable', models.BooleanField()),
                ('attendee', models.ForeignKey(blank=True, to='app.Attendee', null=True)),
            ],
            options={
                'db_table': 'devices_token',
            },
        ),
    ]
