# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0047_auto_20150903_1826'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='requestedbuddy',
            table='requested_buddies',
        ),
    ]
