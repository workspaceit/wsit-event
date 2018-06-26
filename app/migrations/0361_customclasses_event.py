# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0360_pluginpdfbutton'),
    ]

    operations = [
        migrations.AddField(
            model_name='customclasses',
            name='event',
            field=models.ForeignKey(to='app.Events', default=1),
            preserve_default=False,
        ),
    ]
