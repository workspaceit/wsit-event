# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20150819_1448'),
    ]

    operations = [
        migrations.RenameField(
            model_name='locations',
            old_name='location_group',
            new_name='group',
        ),
    ]
