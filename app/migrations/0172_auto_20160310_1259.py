# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0171_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questions',
            name='description',
            field=models.TextField(default=None, null=True),
        ),
    ]