# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0317_registrationgroups_is_show'),
    ]

    operations = [
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('order_number', models.IntegerField()),
                ('cost', models.FloatField()),
                ('rebate_amount', models.FloatField(null=True)),
                ('vat_amount', models.FloatField(null=True)),
                ('due_date', models.DateTimeField()),
                ('status', app.models.OrderStatus(choices=[('open', 'Open'), ('pending', 'Pending'), ('paid', 'Paid'), ('cancelled', 'Cancelled')], default='open', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
                ('created_by', models.ForeignKey(to='app.Users', null=True)),
            ],
            options={
                'db_table': 'orders',
            },
        ),
    ]
