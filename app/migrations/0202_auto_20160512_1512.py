# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0201_menuitem_only_speaker'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendeeMessage',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
            ],
            options={
                'db_table': 'attendee_message',
            },
        ),
        migrations.RemoveField(
            model_name='messagehistory',
            name='attendee',
        ),
        migrations.AddField(
            model_name='attendeemessage',
            name='message',
            field=models.ForeignKey(to='app.MessageHistory'),
        ),
    ]
