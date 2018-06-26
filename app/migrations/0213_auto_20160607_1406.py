# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0212_auto_20160606_1219'),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkpoint',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('questions', models.TextField()),
                ('allow_re_entry', models.BooleanField(default=False)),
                ('is_hide', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(to='app.Users')),
                ('event', models.ForeignKey(to='app.Events')),
                ('filter', models.ForeignKey(null=True, to='app.RuleSet')),
                ('session', models.ForeignKey(null=True, to='app.Session')),
            ],
            options={
                'db_table': 'Checkpoints',
            },
        ),
        migrations.AddField(
            model_name='scan',
            name='status',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='passwordresetrequest',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 8, 14, 6, 42, 957772)),
        ),
        migrations.AddField(
            model_name='scan',
            name='checkpoint',
            field=models.ForeignKey(null=True, to='app.Checkpoint', default=None),
        ),
    ]
