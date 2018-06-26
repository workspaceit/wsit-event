# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0244_importchangestatus'),
    ]

    operations = [
        migrations.RenameField(
            model_name='importchangestatus',
            old_name='import_change_id',
            new_name='import_change',
        ),
    ]
