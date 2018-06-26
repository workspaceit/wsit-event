# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0236_attendee_event'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menupermission',
            name='group',
        ),
    ]
