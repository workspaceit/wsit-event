# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0194_exportstate_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportstate',
            name='event',
            field=models.ForeignKey(to='app.Events', default=11),
            preserve_default=False,
        ),
    ]
