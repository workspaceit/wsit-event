# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0158_auto_20160209_1333'),
    ]

    operations = [
        migrations.CreateModel(
            name='Elements',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('event', models.ForeignKey(to='app.Events')),
            ],
            options={
                'db_table': 'elements',
            },
        ),
    ]
