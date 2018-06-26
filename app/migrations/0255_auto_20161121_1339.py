# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0254_auto_20161118_1558'),
    ]

    operations = [
        migrations.RenameField(
            model_name='seminarsusers',
            old_name='status_evalution',
            new_name='status_evaluation',
        ),
    ]
