# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0192_attendee_checksum_flag'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('file_name', models.CharField(max_length=255)),
                ('status', models.IntegerField(default=3, help_text='0=on progress, 1= found and done, 2=not found')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'export_state',
            },
        ),
    ]
