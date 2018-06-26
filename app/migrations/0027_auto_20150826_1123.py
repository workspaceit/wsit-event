# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_auto_20150826_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='vat',
            field=models.ForeignKey(to='app.Group'),
        ),
    ]
