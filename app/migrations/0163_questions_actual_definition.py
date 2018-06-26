# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0162_pagecontent_element_filter'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='actual_definition',
            field=models.CharField(null=True, max_length=50),
        ),
    ]
