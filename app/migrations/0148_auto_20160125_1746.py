# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0147_auto_20160125_1745'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menupermission',
            old_name='groups',
            new_name='group',
        ),
    ]
