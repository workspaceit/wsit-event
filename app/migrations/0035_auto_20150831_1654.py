# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0034_auto_20150828_1119'),
    ]

    operations = [
        migrations.RenameField(
            model_name='seminarsusers',
            old_name='user',
            new_name='attendee',
        ),
        migrations.RemoveField(
            model_name='seminarsusers',
            name='seminar',
        ),
        migrations.AddField(
            model_name='seminarsusers',
            name='session',
            field=models.ForeignKey(to='app.Session', default=1),
            preserve_default=False,
        ),
    ]
