# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0286_auto_20170418_1613'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='comment',
            field=models.TextField(null=True),
        ),
    ]
