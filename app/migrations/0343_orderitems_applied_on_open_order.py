# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0342_auto_20170921_1225'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitems',
            name='applied_on_open_order',
            field=models.BooleanField(default=True),
        ),
    ]
