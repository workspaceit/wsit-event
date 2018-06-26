# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0099_scan'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('rating', models.IntegerField(max_length=2)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
                ('session', models.ForeignKey(to='app.Session')),
            ],
            options={
                'db_table': 'session_ratings',
            },
        ),
    ]
