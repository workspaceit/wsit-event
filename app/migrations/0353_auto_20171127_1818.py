# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0352_emailcontents_subject_lang'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditorders',
            name='invoice_ref',
            field=models.CharField(null=True, max_length=100),
        ),
        migrations.AddField(
            model_name='orders',
            name='invoice_ref',
            field=models.CharField(null=True, max_length=100),
        ),
        migrations.AddField(
            model_name='payments',
            name='invoice_ref',
            field=models.CharField(null=True, max_length=100),
        ),
    ]
