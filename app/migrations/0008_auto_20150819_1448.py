# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_locations_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact',
            name='location',
        ),
        migrations.AddField(
            model_name='locations',
            name='contacts',
            field=models.TextField(default=None),
        ),
        migrations.DeleteModel(
            name='Contact',
        ),
    ]
