# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0059_booking_broken_up'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsedRule',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('rule', models.ForeignKey(to='app.RuleSet')),
                ('user', models.ForeignKey(related_name='rules', to='app.Users')),
            ],
            options={
                'db_table': 'used_rule',
            },
        ),
    ]
