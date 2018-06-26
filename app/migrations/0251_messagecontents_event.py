# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0250_auto_20161111_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagecontents',
            name='event',
            field=models.ForeignKey(to='app.Events', default=11),
            preserve_default=False,
        ),
    ]
