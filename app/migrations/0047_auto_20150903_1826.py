# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0046_auto_20150903_1706'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestedBuddy',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('exists', models.BooleanField(default=True)),
                ('name', models.CharField(blank=True, max_length=255, default='')),
                ('booking', models.ForeignKey(to='app.Booking')),
                ('buddy', models.ForeignKey(to='app.Attendee', null=True)),
            ],
            options={
                'db_table': 'requested_buddie',
            },
        ),

        migrations.DeleteModel(
            name='RequestedBuddies',
        ),
    ]
