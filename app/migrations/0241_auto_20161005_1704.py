# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0240_menuitem_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='cost',
            field=models.DecimalField(max_digits=8, decimal_places=2, default=None, null=True),
        ),
    ]
