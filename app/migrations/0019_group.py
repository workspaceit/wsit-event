# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_auto_20150824_1106'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('type', app.models.GroupType(choices=[('attendee', 'Attendee'), ('session', 'Session'), ('hotel', 'Hotel'), ('filter', 'Filter'), ('payment', 'Payment')], max_length=50)),
            ],
            options={
                'db_table': 'group',
            },
        ),
    ]
