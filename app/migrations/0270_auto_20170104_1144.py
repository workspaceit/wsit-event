# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0269_auto_20161228_1413'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendeeSubmitButton',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('hit_count', models.IntegerField()),
                ('attendee', models.ForeignKey(to='app.Attendee', null=True)),
            ],
            options={
                'db_table': 'attendee_submit_button',
            },
        ),
        migrations.CreateModel(
            name='PluginSubmitButton',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(to='app.Users')),
                ('page', models.ForeignKey(to='app.PageContent')),
            ],
            options={
                'db_table': 'plugin_submit_button',
            },
        ),
        migrations.AddField(
            model_name='attendeesubmitbutton',
            name='button',
            field=models.ForeignKey(to='app.PluginSubmitButton'),
        ),
    ]
