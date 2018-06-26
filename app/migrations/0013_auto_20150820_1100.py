# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20150820_1050'),
    ]

    operations = [
        migrations.RenameField(
            model_name='locations',
            old_name='contacts_email',
            new_name='contact_email',
        ),
        migrations.RenameField(
            model_name='locations',
            old_name='contacts_name',
            new_name='contact_name',
        ),
        migrations.RenameField(
            model_name='locations',
            old_name='contacts_phone',
            new_name='contact_phone',
        ),
        migrations.RenameField(
            model_name='locations',
            old_name='contacts_web',
            new_name='contact_web',
        ),
    ]
