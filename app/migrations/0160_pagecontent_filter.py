# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0159_elements'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagecontent',
            name='filter',
            field=models.TextField(null=True, default=None),
        ),
    ]
