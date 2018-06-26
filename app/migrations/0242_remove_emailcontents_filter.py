# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0241_auto_20161005_1704'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailcontents',
            name='filter',
        ),
    ]
