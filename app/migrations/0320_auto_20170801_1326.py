# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0319_auto_20170731_1738'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rebates',
            old_name='type',
            new_name='item_type',
        ),
        migrations.AddField(
            model_name='rebates',
            name='rebate_type',
            field=app.models.RebateType(choices=[('percentage', 'Percentage'), ('fixed', 'Fixed sum')], default='fixed', max_length=100),
            preserve_default=False,
        ),
    ]
