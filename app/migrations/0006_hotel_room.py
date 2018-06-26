# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20150818_1627'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('category', models.CharField(max_length=255)),
                ('location', models.ForeignKey(to='app.Locations')),
            ],
            options={
                'db_table': 'hotels',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=255)),
                ('cost', models.DecimalField(max_digits=8, decimal_places=2)),
                ('beds', models.IntegerField()),
                ('vat', models.DecimalField(max_digits=8, decimal_places=2)),
                ('hotel', models.ForeignKey(to='app.Hotel')),
            ],
            options={
                'db_table': 'rooms',
            },
        ),
    ]
