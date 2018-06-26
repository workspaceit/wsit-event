# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0043_auto_20150902_1814'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomAllotment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('total_available', models.IntegerField()),
                ('available_from', models.DateField()),
                ('available_to', models.DateField()),
            ],
            options={
                'db_table': 'room_allotments',
            },
        ),
        migrations.RemoveField(
            model_name='room',
            name='total_rooms',
        ),
        migrations.AddField(
            model_name='roomallotment',
            name='room',
            field=models.ForeignKey(to='app.Room'),
        ),
    ]
