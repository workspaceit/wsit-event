# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20150806_1846'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('contacts_info', models.TextField()),
            ],
            options={
                'db_table': 'contacts',
            },
        ),
        migrations.AddField(
            model_name='locations',
            name='address',
            field=models.TextField(default=None),
        ),
        migrations.AddField(
            model_name='locations',
            name='latitude',
            field=models.CharField(default=None, max_length=50),
        ),
        migrations.AddField(
            model_name='locations',
            name='location_group',
            field=models.CharField(default=None, max_length=255),
        ),
        migrations.AddField(
            model_name='locations',
            name='longitude',
            field=models.CharField(default=None, max_length=50),
        ),
        migrations.AlterField(
            model_name='users',
            name='updated',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name='contact',
            name='location',
            field=models.ForeignKey(to='app.Locations'),
        ),
    ]
