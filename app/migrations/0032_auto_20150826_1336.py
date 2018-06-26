# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_auto_20150826_1335'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='attendeetag',
            table='attendee_tags',
        ),
    ]
