# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_group_event'),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=1024)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('reg_between_start', models.DateField()),
                ('reg_between_end', models.DateField()),
                ('max_attendees', models.IntegerField()),
                ('allow_attendees_queue', models.BooleanField()),
                ('speakers', models.CharField(max_length=1024)),
            ],
        ),
        migrations.AlterModelTable(
            name='group',
            table=None,
        ),
        migrations.AddField(
            model_name='session',
            name='group',
            field=models.ForeignKey(to='app.Group'),
        ),
        migrations.AddField(
            model_name='session',
            name='location',
            field=models.ForeignKey(to='app.Locations'),
        ),
    ]
