# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0138_auto_20160111_1642'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='menuitem',
            table='menu_items',
        ),
    ]
