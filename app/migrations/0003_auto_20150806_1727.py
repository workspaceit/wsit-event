# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20150806_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='updated',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
