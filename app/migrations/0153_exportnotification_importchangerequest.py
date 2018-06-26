# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0152_questionprerequisite'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('file_name', models.CharField(max_length=255, unique=True)),
                ('status', models.SmallIntegerField()),
                ('request_time', models.DateTimeField()),
                ('admin', models.ForeignKey(to='app.Users')),
                ('event', models.ForeignKey(to='app.Events')),
            ],
            options={
                'db_table': 'export_notification',
            },
        ),
        migrations.CreateModel(
            name='ImportChangeRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('changed_data', models.TextField()),
                ('status', models.SmallIntegerField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField(null=True)),
                ('approved_by', models.ForeignKey(related_name='approved_by', to='app.Users', null=True)),
                ('event', models.ForeignKey(to='app.Events')),
                ('imported_by', models.ForeignKey(to='app.Users', related_name='imported_by')),
            ],
            options={
                'db_table': 'import_change_request',
            },
        ),
    ]
