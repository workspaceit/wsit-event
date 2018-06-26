# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0229_auto_20160926_1809'),
    ]

    operations = [
        migrations.AddField(
            model_name='elementdefaultlang',
            name='key',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
