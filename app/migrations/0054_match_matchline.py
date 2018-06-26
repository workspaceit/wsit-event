# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0053_ruleset'),
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('room', models.ForeignKey(to='app.Room')),
            ],
            options={
                'db_table': 'matches',
            },
        ),
        migrations.CreateModel(
            name='MatchLine',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('booking', models.ForeignKey(to='app.Booking')),
                ('match', models.ForeignKey(to='app.Match')),
            ],
            options={
                'db_table': 'match_line',
            },
        ),
    ]
