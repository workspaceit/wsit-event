# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0033_auto_20150827_1711'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='description',
            field=models.TextField(default=None),
        ),
        migrations.AddField(
            model_name='questions',
            name='group',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
