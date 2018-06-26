# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_auto_20150824_1636'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='group',
            table='groups',
        ),
        migrations.AlterModelTable(
            name='session',
            table='sessions',
        ),
    ]
