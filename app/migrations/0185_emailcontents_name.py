# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0184_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailcontents',
            name='name',
            field=models.CharField(max_length=255, default=''),
            preserve_default=False,
        ),
    ]
