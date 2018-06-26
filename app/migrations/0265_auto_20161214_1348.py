# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0264_auto_20161207_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cookie',
            name='created_at',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='cookiepage',
            name='visit_date',
            field=models.DateTimeField(),
        ),
    ]
