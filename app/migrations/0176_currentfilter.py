# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0175_currentevent'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentFilter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('admin', models.ForeignKey(to='app.Users')),
                ('event', models.ForeignKey(to='app.Events')),
                ('filter', models.ForeignKey(to='app.RuleSet')),
            ],
            options={
                'db_table': 'current_filter',
            },
        ),
    ]
