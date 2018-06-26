# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0312_deletedhistory_registration_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
