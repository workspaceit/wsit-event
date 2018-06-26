# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0161_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagecontent',
            name='element_filter',
            field=models.TextField(null=True, default=None),
        ),
    ]
