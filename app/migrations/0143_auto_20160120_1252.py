# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0142_auto_20160120_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='uid_include',
            field=models.BooleanField(default=False),
        ),
    ]
