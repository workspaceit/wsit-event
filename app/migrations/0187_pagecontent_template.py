# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0186_emailtemplates_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagecontent',
            name='template',
            field=models.ForeignKey(default=1, to='app.EmailTemplates'),
            preserve_default=False,
        ),
    ]
