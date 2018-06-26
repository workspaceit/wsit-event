# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0200_auto_20160426_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='only_speaker',
            field=models.BooleanField(default=False),
        ),
    ]
