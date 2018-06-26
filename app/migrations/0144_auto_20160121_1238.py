# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0143_auto_20160120_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagecontent',
            name='url',
            field=models.CharField(unique=True, null=True, max_length=255),
        ),
    ]
