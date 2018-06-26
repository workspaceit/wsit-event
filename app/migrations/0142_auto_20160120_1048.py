# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0141_auto_20160118_1619'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='uid_include',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='menuitem',
            name='url',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
