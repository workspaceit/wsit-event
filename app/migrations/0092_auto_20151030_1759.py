# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0091_auto_20151030_1758'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatparticipant',
            old_name='chat_room_id',
            new_name='chat_room',
        ),
    ]
