# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0255_auto_20161121_1339'),
    ]

    operations = [
        migrations.RenameField(
            model_name='seminarsusers',
            old_name='status_evaluation',
            new_name='status_socket_evaluation',
        ),
        migrations.RenameField(
            model_name='seminarsusers',
            old_name='status_nextup',
            new_name='status_socket_nextup',
        ),
        migrations.AddField(
            model_name='notification',
            name='status_socket_message',
            field=models.BooleanField(default=False),
        ),
    ]
