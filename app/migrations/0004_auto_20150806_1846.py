# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20150806_1727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
