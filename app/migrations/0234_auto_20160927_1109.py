# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0233_auto_20160927_1108'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='attendeegroups',
            table='attendee_groups',
        ),
    ]
