# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0035_auto_20150831_1654'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('check_in_time', models.DateField()),
                ('check_out_time', models.DateField()),
                ('room', models.ForeignKey(to='app.Room')),
            ],
            options={
                'db_table': 'bookings',
            },
        ),
        migrations.CreateModel(
            name='RoomAttendee',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
                ('booking', models.ForeignKey(to='app.Booking')),
            ],
            options={
                'db_table': 'room_attendees',
            },
        ),
    ]
