# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0303_group_name_lang'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotel',
            name='name_lang',
            field=models.TextField(null=True, default=None),
        ),
        migrations.AddField(
            model_name='locations',
            name='address_lang',
            field=models.TextField(null=True, default=None),
        ),
        migrations.AddField(
            model_name='locations',
            name='contact_name_lang',
            field=models.TextField(null=True, default=None),
        ),
        migrations.AddField(
            model_name='locations',
            name='description_lang',
            field=models.TextField(null=True, default=None),
        ),
        migrations.AddField(
            model_name='locations',
            name='name_lang',
            field=models.TextField(null=True, default=None),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='title_lang',
            field=models.TextField(null=True, default=None),
        ),
        migrations.AddField(
            model_name='option',
            name='option_lang',
            field=models.TextField(null=True, default=None),
        ),
        migrations.AddField(
            model_name='questions',
            name='description_lang',
            field=models.TextField(null=True, default=None),
        ),
        migrations.AddField(
            model_name='questions',
            name='title_lang',
            field=models.TextField(null=True, default=None),
        ),
        migrations.AddField(
            model_name='room',
            name='description_lang',
            field=models.TextField(null=True, default=None),
        ),
        migrations.AddField(
            model_name='session',
            name='description_lang',
            field=models.TextField(null=True, default=None),
        ),
        migrations.AddField(
            model_name='session',
            name='name_lang',
            field=models.TextField(null=True, default=None),
        ),
        migrations.AddField(
            model_name='travel',
            name='description_lang',
            field=models.TextField(null=True, default=None),
        ),
        migrations.AddField(
            model_name='travel',
            name='name_lang',
            field=models.TextField(null=True, default=None),
        ),
    ]
