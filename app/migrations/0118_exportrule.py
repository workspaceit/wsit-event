# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0117_travelboundrelation'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportRule',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('preset', models.TextField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('modified_at', models.DateField(auto_now=True)),
                ('created_by', models.ForeignKey(to='app.Users')),
                ('group', models.ForeignKey(to='app.Group')),
            ],
            options={
                'db_table': 'export_rules',
            },
        ),
    ]
