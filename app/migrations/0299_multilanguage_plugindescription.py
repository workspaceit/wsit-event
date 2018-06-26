# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0298_questions_show_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='MultiLanguage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('general_id', models.IntegerField()),
                ('type', app.models.MultiLanguageType(choices=[('menu_title', 'Menu Title'), ('question_label', 'Question Label'), ('question_description', 'Question Description'), ('session_name', 'Session Name'), ('session_description', 'Session Description'), ('travel_name', 'Travel Name'), ('travel_description', 'Travel Description'), ('location_name', 'Location Name'), ('location_description', 'Location Description'), ('location_address', 'Location Address'), ('contact_name', 'Contact Name'), ('hotel_name', 'Hotel Name'), ('hotel_room_description', 'Hotel Room Description'), ('group_name', 'Group Name'), ('question_option', 'Question Option')], max_length=100)),
                ('value', models.TextField()),
                ('language', models.ForeignKey(to='app.Presets')),
            ],
            options={
                'db_table': 'multi_language',
            },
        ),
        migrations.CreateModel(
            name='PluginDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('box_id', models.IntegerField()),
                ('value', models.TextField()),
                ('element', models.ForeignKey(to='app.Elements')),
                ('language', models.ForeignKey(null=True, to='app.Presets')),
                ('page', models.ForeignKey(to='app.PageContent')),
            ],
            options={
                'db_table': 'plugin_description',
            },
        ),
    ]
