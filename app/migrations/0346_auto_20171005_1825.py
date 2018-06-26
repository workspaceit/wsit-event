# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0345_sessionclasses'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditUsages',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('order_number', models.IntegerField()),
                ('cost', models.FloatField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('credit_order', models.ForeignKey(to='app.CreditOrders')),
            ],
            options={
                'db_table': 'credit_usages',
            },
        ),
        migrations.AlterField(
            model_name='orders',
            name='due_date',
            field=models.DateTimeField(null=True),
        ),
    ]
