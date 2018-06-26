# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0271_auto_20170105_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='elementsquestions',
            name='question_key',
            field=models.CharField(max_length=1000, default=''),
            preserve_default=False,
        ),
    ]
