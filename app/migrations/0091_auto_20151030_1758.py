# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0090_chatparticipant'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatparticipant',
            old_name='attendee_id',
            new_name='attendee',
        ),
        migrations.RenameField(
            model_name='chatparticipant',
            old_name='session_id',
            new_name='session',
        ),
    ]
