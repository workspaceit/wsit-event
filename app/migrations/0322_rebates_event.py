# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0321_auto_20170801_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='rebates',
            name='event',
            field=models.ForeignKey(null=True, to='app.Events'),
        ),
    ]
