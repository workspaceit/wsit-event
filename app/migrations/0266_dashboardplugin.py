# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0265_auto_20161214_1348'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardPlugin',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('sort', models.TextField()),
                ('modified_at', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(to='app.Events')),
                ('modified_by', models.ForeignKey(to='app.Users')),
            ],
            options={
                'db_table': 'dashboard_plugin',
            },
        ),
    ]
