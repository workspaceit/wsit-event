# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0295_auto_20170511_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='deletedhistory',
            name='photo',
            field=models.ForeignKey(null=True, to='app.Photo'),
        ),
    ]
