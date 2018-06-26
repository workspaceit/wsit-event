# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0270_auto_20170104_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elementsanswers',
            name='answer',
            field=models.TextField(),
        ),
    ]
