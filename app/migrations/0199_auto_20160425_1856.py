# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0198_menuitem_available_offline'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='content',
            field=models.ForeignKey(to='app.PageContent', blank=True, null=True),
        ),
    ]
