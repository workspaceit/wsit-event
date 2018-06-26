# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0336_auto_20170911_1751'),
    ]

    operations = [
        migrations.RenameField(
            model_name='creditorders',
            old_name='cost',
            new_name='cost_excluding_vat',
        ),
        migrations.AddField(
            model_name='creditorders',
            name='cost_including_vat',
            field=models.FloatField(default=0),
        ),
    ]
