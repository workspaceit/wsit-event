# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0050_auto_20150907_1350'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomAllotment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('allotments', models.IntegerField()),
                ('available_date', models.DateField()),
                ('room', models.ForeignKey(to='app.Room')),
            ],
            options={
                'db_table': 'room_allotments',
            },
        ),
    ]
