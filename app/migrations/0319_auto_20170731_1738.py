# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0318_orders'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditOrders',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('order_number', models.IntegerField()),
                ('cost', models.FloatField()),
                ('type', app.models.OrderItemType(max_length=100, choices=[('session', 'Session'), ('hotel', 'Hotel'), ('travel', 'Travel'), ('rebate', 'Rebate')])),
                ('item_name', models.CharField(max_length=255)),
                ('status', app.models.OrderStatus(max_length=100, choices=[('open', 'Open'), ('pending', 'Pending'), ('paid', 'Paid'), ('cancelled', 'Cancelled')], default='open')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(to='app.Users', null=True)),
                ('order', models.ForeignKey(to='app.Orders')),
            ],
            options={
                'db_table': 'credit_orders',
            },
        ),
        migrations.CreateModel(
            name='OrderItems',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('item_type', app.models.OrderItemType(max_length=100, choices=[('session', 'Session'), ('hotel', 'Hotel'), ('travel', 'Travel'), ('rebate', 'Rebate')])),
                ('item_id', models.IntegerField()),
                ('cost', models.FloatField()),
                ('rebate_amount', models.FloatField(null=True)),
                ('vat_rate', models.FloatField()),
                ('order', models.ForeignKey(to='app.Orders')),
            ],
            options={
                'db_table': 'order_items',
            },
        ),
        migrations.CreateModel(
            name='Payments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('method', app.models.PaymentMethod(max_length=100, choices=[('dibs', 'Dibs'), ('admin', 'Admin')])),
                ('amount', models.FloatField()),
                ('details', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(to='app.Users', null=True)),
                ('order', models.ForeignKey(to='app.Orders')),
            ],
            options={
                'db_table': 'payments',
            },
        ),
        migrations.CreateModel(
            name='Rebates',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('type', app.models.OrderItemType(max_length=100, choices=[('session', 'Session'), ('hotel', 'Hotel'), ('travel', 'Travel'), ('rebate', 'Rebate')])),
                ('value', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(to='app.Users')),
            ],
            options={
                'db_table': 'rebates',
            },
        ),
        migrations.AddField(
            model_name='orderitems',
            name='rebate',
            field=models.ForeignKey(to='app.Rebates', null=True),
        ),
    ]
