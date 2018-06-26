# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0297_remove_menuitem_named_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='show_description',
            field=models.BooleanField(default=False),
        ),
    ]
