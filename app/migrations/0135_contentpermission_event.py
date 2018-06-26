# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0134_auto_20160106_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentpermission',
            name='event',
            field=models.ForeignKey(default=1, to='app.Events'),
            preserve_default=False,
        ),
    ]
