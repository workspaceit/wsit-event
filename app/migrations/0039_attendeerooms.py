# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0038_seminarspeakers'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendeeRooms',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('check_in', models.DateField()),
                ('check_out', models.DateField()),
                ('attendee', models.ForeignKey(to='app.Attendee')),
                ('room', models.ForeignKey(to='app.Room')),
            ],
        ),
    ]
