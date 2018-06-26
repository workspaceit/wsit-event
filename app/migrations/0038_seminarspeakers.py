# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0037_attendee_event'),
    ]

    operations = [
        migrations.CreateModel(
            name='SeminarSpeakers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('session', models.ForeignKey(to='app.Session')),
                ('speaker', models.ForeignKey(to='app.Attendee')),
            ],
            options={
                'db_table': 'seminars_has_speakers',
            },
        ),
    ]
