# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0307_generaltag_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locations',
            name='name',
            field=models.CharField(max_length=45),
        ),
    ]
