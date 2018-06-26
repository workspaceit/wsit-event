# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0351_stylesheet_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailcontents',
            name='subject_lang',
            field=models.TextField(null=True, default=None),
        ),
    ]
