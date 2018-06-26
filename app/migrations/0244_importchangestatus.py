# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0243_customclasses_pagecontentclasses'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportChangeStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('filename', models.TextField()),
                ('message', models.TextField(null=True)),
                ('status', models.SmallIntegerField()),
                ('import_change_id', models.ForeignKey(null=True, to='app.ImportChangeRequest')),
            ],
            options={
                'db_table': 'import_change_status',
            },
        ),
    ]
