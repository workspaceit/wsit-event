# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0268_auto_20161228_1411'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='cookie',
            table='cookie',
        ),
        migrations.AlterModelTable(
            name='cookiepage',
            table='cookie_page',
        ),
    ]
