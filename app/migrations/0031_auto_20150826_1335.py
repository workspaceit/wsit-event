# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0030_auto_20150826_1334'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='attendeetag',
            table='attendee_tag',
        ),
        migrations.AlterModelTable(
            name='tag',
            table='tags',
        ),
    ]
