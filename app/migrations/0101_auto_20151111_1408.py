# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0100_photo_is_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='thumb_image',
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='is_approved',
            field=models.IntegerField(default=0),
        ),
    ]
