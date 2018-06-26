# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0316_emaillanguagecontents_messagelanguagecontents'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationgroups',
            name='is_show',
            field=models.BooleanField(default=True),
        ),
    ]
