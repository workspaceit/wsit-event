# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0063_auto_20150912_1142'),
    ]

    operations = [
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('option', models.CharField(max_length=255)),
                ('question', models.ForeignKey(to='app.Questions')),
            ],
            options={
                'db_table': 'options',
            },
        ),
    ]
