# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0260_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='PagePermission',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('page', models.ForeignKey(to='app.PageContent')),
                ('rule', models.ForeignKey(default=None, null=True, to='app.RuleSet')),
            ],
            options={
                'db_table': 'page_permission',
            },
        ),
    ]
