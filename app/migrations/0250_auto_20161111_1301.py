# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0249_elements_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elements',
            name='slug',
            field=models.CharField(max_length=255),
        ),
    ]
