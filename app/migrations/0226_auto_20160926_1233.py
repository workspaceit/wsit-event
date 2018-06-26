# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0225_checkpoint_defaults'),
    ]

    operations = [
        migrations.CreateModel(
            name='ElementDefaultLang',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=100)),
                ('name', models.TextField()),
                ('value', models.TextField()),
                ('element', models.ForeignKey(to='app.Elements')),
            ],
            options={
                'db_table': 'element_default_lang',
            },
        ),
        migrations.CreateModel(
            name='ElementPresetLang',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('value', models.TextField()),
                ('element_default_lang', models.ForeignKey(to='app.ElementDefaultLang')),
            ],
            options={
                'db_table': 'element_preset_lang',
            },
        ),
        migrations.CreateModel(
            name='PresetEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('event', models.ForeignKey(to='app.Events')),
            ],
            options={
                'db_table': 'preset_event',
            },
        ),
        migrations.CreateModel(
            name='Presets',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('preset_name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'presets',
            },
        ),
        migrations.AddField(
            model_name='presetevent',
            name='preset',
            field=models.ForeignKey(to='app.Presets'),
        ),
        migrations.AddField(
            model_name='elementpresetlang',
            name='preset',
            field=models.ForeignKey(to='app.Presets'),
        ),
    ]
