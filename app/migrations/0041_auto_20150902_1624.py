# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0040_auto_20150902_1621'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendeeRoom',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('check_in', models.DateField()),
                ('check_out', models.DateField()),
                ('attendee', models.ForeignKey(to='app.Attendee')),
                ('room', models.ForeignKey(to='app.Room')),
            ],
            options={
                'db_table': 'attendee_rooms',
            },
        ),
        migrations.RemoveField(
            model_name='attendeerooms',
            name='attendee',
        ),
        migrations.RemoveField(
            model_name='attendeerooms',
            name='room',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='check_in_time',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='check_out_time',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='room',
        ),
        migrations.DeleteModel(
            name='AttendeeRooms',
        ),
        migrations.AddField(
            model_name='booking',
            name='attendee_room',
            field=models.ForeignKey(to='app.AttendeeRoom', default=1),
            preserve_default=False,
        ),
    ]
