# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0311_auto_20170703_1229'),
    ]

    operations = [
        migrations.AddField(
            model_name='deletedhistory',
            name='registration_group',
            field=models.ForeignKey(null=True, to='app.RegistrationGroups'),
        ),
    ]
