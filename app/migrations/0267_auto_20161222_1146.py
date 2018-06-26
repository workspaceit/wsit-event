# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0266_dashboardplugin'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dashboardplugin',
            old_name='sort',
            new_name='setting_data',
        ),
    ]
