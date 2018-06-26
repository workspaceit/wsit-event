# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0239_auto_20161004_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='event',
            field=models.ForeignKey(default=None, null=True, to='app.Events'),
        ),
    ]
