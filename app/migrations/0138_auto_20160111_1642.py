# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0137_setting_event'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('title', models.CharField(max_length=50)),
                ('url', models.CharField(blank=True, max_length=255)),
                ('named_url', models.CharField(blank=True, max_length=255)),
                ('level', models.IntegerField(default=0)),
                ('rank', models.IntegerField(default=0)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('is_visible', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'menu_item',
            },
        ),
        migrations.AlterField(
            model_name='group',
            name='type',
            field=app.models.GroupType(max_length=50, choices=[('attendee', 'Attendee'), ('session', 'Session'), ('hotel', 'Hotel'), ('filter', 'Filter'), ('payment', 'Payment'), ('question', 'Question'), ('location', 'Location'), ('travel', 'Travel'), ('export_filter', 'Export Filter'), ('menu', 'Menu')]),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='group',
            field=models.ForeignKey(to='app.Group'),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, to='app.MenuItem'),
        ),
    ]
