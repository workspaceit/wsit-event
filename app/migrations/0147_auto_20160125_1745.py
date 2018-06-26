# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0146_auto_20160125_1744'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menupermission',
            old_name='group',
            new_name='groups',
        ),
    ]
