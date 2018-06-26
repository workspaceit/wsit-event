# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0232_auto_20160927_1012'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendeeGroups',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
                ('group', models.ForeignKey(to='app.Group')),
            ],
        ),
        migrations.RemoveField(
            model_name='elementdefaultlang',
            name='key',
        ),
        migrations.AddField(
            model_name='elementdefaultlang',
            name='lang_key',
            field=models.CharField(max_length=100, default=''),
            preserve_default=False,
        ),
    ]
