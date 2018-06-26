# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0135_contentpermission_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
