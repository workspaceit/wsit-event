# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0263_auto_20161207_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cookie',
            name='created_at',
            field=models.DateField(null=True, auto_now_add=True),
        ),
    ]
