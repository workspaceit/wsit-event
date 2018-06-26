# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0346_auto_20171005_1825'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('currency', models.CharField(max_length=10)),
                ('merchant_id', models.CharField(max_length=100)),
                ('payment_types', models.CharField(max_length=100)),
                ('key1', models.CharField(max_length=100)),
                ('key2', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(to='app.Users')),
                ('event', models.ForeignKey(to='app.Events')),
            ],
            options={
                'db_table': 'payment_settings',
            },
        ),
    ]
