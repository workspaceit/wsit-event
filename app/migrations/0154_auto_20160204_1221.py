# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0153_auto_20160203_1220'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='max_character',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='questions',
            name='min_character',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='questions',
            name='question_class',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='questions',
            name='regular_expression',
            field=models.TextField(default=None, null=True),
        ),
    ]
