# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0154_auto_20160204_1221'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagecontent',
            name='login_required',
            field=models.BooleanField(default=False),
        ),
    ]
