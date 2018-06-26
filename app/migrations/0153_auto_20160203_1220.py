# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0152_questionprerequisite'),
    ]

    operations = [
        migrations.RenameField(
            model_name='requestedbuddy',
            old_name='name',
            new_name='email',
        ),
    ]
