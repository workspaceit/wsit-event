# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0180_emailtemplates'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailtemplates',
            name='name',
            field=models.CharField(default='a', max_length=255),
            preserve_default=False,
        ),
    ]
