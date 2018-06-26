# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0206_auto_20160513_1652'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisibleColumns',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('visible_columns', models.TextField(null=True, default=None)),
                ('type', app.models.ColumnType(choices=[('session', 'Session'), ('hotel', 'Hotel')], max_length=50)),
                ('admin', models.ForeignKey(to='app.Users')),
                ('event', models.ForeignKey(to='app.Events')),
            ],
            options={
                'db_table': 'visible_columns',
            },
        ),
    ]
