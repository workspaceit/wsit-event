# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0359_auto_20180111_1200'),
    ]

    operations = [
        migrations.CreateModel(
            name='PluginPdfButton',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(to='app.Users')),
                ('page', models.ForeignKey(to='app.PageContent')),
            ],
            options={
                'db_table': 'plugin_pdf_button',
            },
        ),
    ]
