# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0267_auto_20161222_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cookiepage',
            name='visit_date',
            field=models.DateField(),
        ),
    ]
