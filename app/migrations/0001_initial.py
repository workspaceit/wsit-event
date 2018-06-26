# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Answers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('value', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'answers',
            },
        ),
        migrations.CreateModel(
            name='Events',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('date', models.DateTimeField()),
                ('name', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'events',
            },
        ),
        migrations.CreateModel(
            name='Locations',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=45)),
                ('event', models.ForeignKey(to='app.Events')),
            ],
            options={
                'db_table': 'locations',
            },
        ),
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('title', models.CharField(max_length=45)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=45)),
                ('required', models.BooleanField(default=True)),
                ('event', models.ForeignKey(to='app.Events')),
            ],
            options={
                'db_table': 'questions',
            },
        ),
        migrations.CreateModel(
            name='Seminars',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('date', models.DateTimeField()),
                ('name', models.CharField(max_length=45)),
                ('event', models.ForeignKey(to='app.Events')),
            ],
            options={
                'db_table': 'seminars',
            },
        ),
        migrations.CreateModel(
            name='SeminarsUsers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('seminar', models.ForeignKey(to='app.Seminars')),
            ],
            options={
                'db_table': 'seminars_has_users',
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('firstname', models.CharField(max_length=45)),
                ('lastname', models.CharField(max_length=45)),
                ('company', models.CharField(max_length=45)),
                ('email', models.CharField(max_length=45)),
                ('password', models.CharField(max_length=45)),
                ('phonenumber', models.CharField(max_length=45)),
                ('role', app.models.UserRoles(choices=[('student', 'Student'), ('participant', 'Participant'), ('speaker', 'Speaker'), ('vip', 'Vip')], max_length=20)),
                ('type', app.models.UserTypes(choices=[('super_admin', 'SuperAdmin'), ('admin', 'Admin'), ('user', 'User'), ('guest', 'Guest')], max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.AddField(
            model_name='seminarsusers',
            name='user',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='answers',
            name='question',
            field=models.ForeignKey(to='app.Questions'),
        ),
        migrations.AddField(
            model_name='answers',
            name='user',
            field=models.ForeignKey(to='app.Users'),
        ),
    ]
