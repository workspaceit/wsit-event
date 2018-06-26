# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0119_auto_20151211_1624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='travel',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
