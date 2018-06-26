# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0094_sessiontags'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='sessiontags',
            table='session_has_tags',
        ),
    ]
