# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0302_auto_20170523_1328'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='name_lang',
            field=models.TextField(default=None, null=True),
        ),
    ]
