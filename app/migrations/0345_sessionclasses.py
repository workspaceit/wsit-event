# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0344_orderitems_rebate_is_deleted'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionClasses',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('classname', models.ForeignKey(to='app.CustomClasses')),
                ('session', models.ForeignKey(to='app.Session')),
            ],
            options={
                'db_table': 'session_has_classes',
            },
        ),
    ]
