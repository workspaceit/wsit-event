# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0045_group_group_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestedBuddies',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('exists', models.BooleanField(default=True)),
                ('name', models.CharField(default='', blank=True, max_length=255)),
            ],
            options={
                'db_table': 'requested_buddies',
            },
        ),
        migrations.RemoveField(
            model_name='attendeeroom',
            name='attendee',
        ),
        migrations.RemoveField(
            model_name='attendeeroom',
            name='room',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='attendee_room',
        ),
        migrations.AddField(
            model_name='booking',
            name='attendee',
            field=models.ForeignKey(to='app.Attendee', default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='check_in',
            field=models.DateField(default=datetime.datetime(2015, 9, 3, 11, 5, 49, 564681, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='check_out',
            field=models.DateField(default=datetime.datetime(2015, 9, 3, 11, 5, 57, 652386, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='room',
            field=models.ForeignKey(to='app.Room', default=1),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='AttendeeRoom',
        ),
        migrations.AddField(
            model_name='requestedbuddies',
            name='booking',
            field=models.ForeignKey(to='app.Booking'),
        ),
        migrations.AddField(
            model_name='requestedbuddies',
            name='buddy',
            field=models.ForeignKey(to='app.Attendee'),
        ),
    ]
