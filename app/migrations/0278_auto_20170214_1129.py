# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0277_auto_20170124_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='vat',
            field=models.ForeignKey(null=True, to='app.Group'),
        ),
    ]
