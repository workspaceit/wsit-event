# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0168_pageimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='StyleSheet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('style', models.TextField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(default=None, to='app.Users')),
                ('event', models.ForeignKey(to='app.Events')),
            ],
            options={
                'db_table': 'event_stylesheets',
            },
        ),
    ]
