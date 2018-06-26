# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0234_auto_20160927_1109'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendee',
            name='group',
        ),
    ]
