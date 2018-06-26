# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0052_auto_20150907_1728'),
    ]

    operations = [
        migrations.CreateModel(
            name='RuleSet',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('preset', models.TextField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('modified_at', models.DateField(auto_now=True)),
                ('created_by', models.ForeignKey(to='app.Users')),
            ],
            options={
                'db_table': 'rule_set',
            },
        ),
    ]
