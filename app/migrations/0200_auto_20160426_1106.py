# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0199_auto_20160425_1856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagecontent',
            name='url',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
