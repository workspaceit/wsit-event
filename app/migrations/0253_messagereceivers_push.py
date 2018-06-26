# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0252_auto_20161115_1614'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagereceivers',
            name='push',
            field=models.BooleanField(default=False),
        ),
    ]
