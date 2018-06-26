# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0168_pageimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='default_answer',
            field=models.TextField(default=None, null=True),
        ),
    ]
