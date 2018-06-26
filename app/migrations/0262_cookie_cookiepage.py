# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0261_pagepermission'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cookie',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('cookie_key', models.TextField()),
                ('created', models.DateTimeField()),
            ],
            options={
                'db_table': 'hitcount_cookie',
            },
        ),
        migrations.CreateModel(
            name='CookiePage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('visit_count', models.IntegerField()),
                ('visit_date', models.DateField()),
                ('cookie', models.ForeignKey(to='app.Cookie')),
                ('page', models.ForeignKey(to='app.PageContent')),
            ],
            options={
                'db_table': 'hitcount_cookie_page',
            },
        ),
    ]
