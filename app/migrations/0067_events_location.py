# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0066_auto_20150914_0846'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='location',
            field=models.ForeignKey(default=1, to='app.Locations'),
            preserve_default=False,
        ),
    ]
