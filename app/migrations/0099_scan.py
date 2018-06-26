# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0098_photo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scan',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('scan_time', models.DateTimeField(auto_now_add=True)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
            ],
            options={
                'db_table': 'scans',
            },
        ),
    ]
