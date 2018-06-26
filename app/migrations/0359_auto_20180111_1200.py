# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0358_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtemplates',
            name='category',
            field=app.models.TemplateCategories(max_length=25, choices=[('web_pages', 'Web Pages'), ('email_templates', 'Email Templates'), ('invoices', 'Invoices'), ('pdf', 'Pdf')]),
        ),
    ]
