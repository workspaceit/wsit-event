# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0100_sessionrating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionrating',
            name='rating',
            field=models.IntegerField(),
        ),
    ]
