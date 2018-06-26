# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0115_auto_20151204_1458'),
    ]

    operations = [
        migrations.CreateModel(
            name='Travel',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('description', models.TextField()),
                ('departure', models.DateTimeField()),
                ('arrival', models.DateTimeField()),
                ('reg_between_start', models.DateField()),
                ('reg_between_end', models.DateField()),
                ('travel_bound', app.models.TravelBound(max_length=20, choices=[('homebound', 'HomeBound'), ('outbound', 'OutBound')])),
                ('max_attendees', models.IntegerField()),
                ('allow_attendees_queue', models.BooleanField(default=False)),
                ('group', models.ForeignKey(to='app.Group')),
                ('location', models.ForeignKey(to='app.Locations')),
            ],
            options={
                'db_table': 'travels',
            },
        ),
        migrations.CreateModel(
            name='TravelAttendee',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('status', app.models.AttendeeSessionStatus(max_length=20, default='attending', choices=[('attending', 'Attending'), ('in-queue', 'In Cue'), ('not-attending', 'Not Attending'), ('deciding', 'Deciding')])),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('queue_order', models.IntegerField(default=1)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
                ('travel', models.ForeignKey(to='app.Travel')),
            ],
            options={
                'db_table': 'travel_has_attendees',
            },
        ),
        migrations.CreateModel(
            name='TravelTag',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
            ],
            options={
                'db_table': 'travel_has_tags',
            },
        ),
        migrations.AlterField(
            model_name='generaltag',
            name='category',
            field=app.models.TagType(max_length=50, default='session', choices=[('session', 'Session'), ('hotel', 'Hotel'), ('room', 'Room'), ('travel', 'Travel')]),
        ),
        migrations.AddField(
            model_name='traveltag',
            name='tag',
            field=models.ForeignKey(to='app.GeneralTag'),
        ),
        migrations.AddField(
            model_name='traveltag',
            name='travel',
            field=models.ForeignKey(to='app.Travel'),
        ),
    ]
