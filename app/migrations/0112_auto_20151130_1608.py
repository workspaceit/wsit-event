# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0111_auto_20151127_1727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seminarsusers',
            name='created',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
