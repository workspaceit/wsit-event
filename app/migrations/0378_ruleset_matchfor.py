# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0377_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='ruleset',
            name='matchfor',
            field=models.CharField(null=True, max_length=1),
        ),
    ]
