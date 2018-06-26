# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0189_auto_20160405_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='accept_login',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='events',
            name='is_show',
            field=models.BooleanField(default=True),
        ),
    ]
