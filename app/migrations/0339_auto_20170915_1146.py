# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0338_auto_20170915_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityhistory',
            name='category',
            field=app.models.ActivityCategoryType(max_length=50, choices=[('event', 'Event'), ('session', 'Session'), ('question', 'Question'), ('travel', 'Travel'), ('room', 'Room'), ('message', 'Message'), ('profile', 'Profile'), ('push_notification', 'Push_notification'), ('group', 'Group'), ('tag', 'Tag'), ('package', 'Package'), ('checkpoint', 'Checkpoint'), ('photo', 'Photo'), ('registration_group', 'Registration_group'), ('rebate', 'Rebate'), ('order', 'Order'), ('order_item', 'Order Item'), ('credit_order', 'Credit Order')]),
        ),
        migrations.AlterField(
            model_name='deletedhistory',
            name='category',
            field=app.models.ActivityCategoryType(max_length=50, choices=[('event', 'Event'), ('session', 'Session'), ('question', 'Question'), ('travel', 'Travel'), ('room', 'Room'), ('message', 'Message'), ('profile', 'Profile'), ('push_notification', 'Push_notification'), ('group', 'Group'), ('tag', 'Tag'), ('package', 'Package'), ('checkpoint', 'Checkpoint'), ('photo', 'Photo'), ('registration_group', 'Registration_group'), ('rebate', 'Rebate'), ('order', 'Order'), ('order_item', 'Order Item'), ('credit_order', 'Credit Order')]),
        ),
    ]
