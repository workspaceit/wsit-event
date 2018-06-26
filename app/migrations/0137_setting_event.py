# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0136_auto_20160106_1827'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='event',
            field=models.ForeignKey(to='app.Events', default=1),
            preserve_default=False,
        ),
    ]
