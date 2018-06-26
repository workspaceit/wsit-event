# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0335_auto_20170911_1603'),
    ]

    operations = [
        migrations.RenameField(
            model_name='creditorders',
            old_name='cost_excluding_vat',
            new_name='cost',
        ),
        migrations.RemoveField(
            model_name='creditorders',
            name='cost_including_vat',
        ),
    ]
