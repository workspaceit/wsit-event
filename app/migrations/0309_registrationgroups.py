# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0308_auto_20170621_1513'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationGroups',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=256)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(to='app.Events')),
            ],
            options={
                'db_table': 'registration_groups',
            },
        ),
    ]
