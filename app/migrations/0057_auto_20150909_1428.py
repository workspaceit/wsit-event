# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0056_auto_20150909_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matchline',
            name='match',
            field=models.ForeignKey(related_name='lines', to='app.Match'),
        ),
    ]
