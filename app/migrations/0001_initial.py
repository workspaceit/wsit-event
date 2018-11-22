# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import app.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('activity_type', app.models.ActivityHistoryType(choices=[('update', 'Update'), ('delete', 'Delete'), ('register', 'Register'), ('message', 'Message'), ('offline', 'Offline Download'), ('check-in', 'Check In')], max_length=50)),
                ('category', app.models.ActivityCategoryType(choices=[('event', 'Event'), ('session', 'Session'), ('question', 'Question'), ('travel', 'Travel'), ('room', 'Room'), ('message', 'Message'), ('profile', 'Profile'), ('push_notification', 'Push_notification'), ('group', 'Group'), ('tag', 'Tag'), ('package', 'Package'), ('checkpoint', 'Checkpoint'), ('photo', 'Photo'), ('registration_group', 'Registration_group'), ('rebate', 'Rebate'), ('order', 'Order'), ('order_item', 'Order Item'), ('credit_order', 'Credit Order'), ('credit_usage', 'Credit Usage'), ('payment', 'Payment')], max_length=50)),
                ('old_value', models.TextField()),
                ('new_value', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('activity_message', models.TextField(null=True)),
            ],
            options={
                'db_table': 'activity_history',
            },
        ),
        migrations.CreateModel(
            name='Answers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('value', models.TextField()),
            ],
            options={
                'db_table': 'answers',
            },
        ),
        migrations.CreateModel(
            name='Attendee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('firstname', models.CharField(max_length=50)),
                ('lastname', models.CharField(max_length=45)),
                ('company', models.CharField(max_length=45)),
                ('email', models.CharField(max_length=45)),
                ('password', models.CharField(max_length=500)),
                ('phonenumber', models.CharField(max_length=45)),
                ('type', app.models.AttendeeTypes(choices=[('user', 'User'), ('guest', 'Guest')], default='user', max_length=50)),
                ('tag', models.CharField(max_length=255)),
                ('checksum', models.TextField(null=True)),
                ('checksum_flag', models.BooleanField(default=False)),
                ('status', app.models.AttendeeStatus(choices=[('canceled', 'Canceled'), ('registered', 'Registered'), ('pending', 'Pending')], default='registered', max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('avatar', models.CharField(max_length=255)),
                ('secret_key', models.CharField(max_length=50, unique=True, null=True)),
                ('bid', models.CharField(max_length=50, unique=True, null=True)),
                ('push_notification_status', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'attendees',
            },
        ),
        migrations.CreateModel(
            name='AttendeeGroups',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
            ],
            options={
                'db_table': 'attendee_groups',
            },
        ),
        migrations.CreateModel(
            name='AttendeePasswordResetRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('hash_code', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expired_at', models.DateTimeField(default=None)),
                ('already_used', models.BooleanField(default=False)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
            ],
            options={
                'db_table': 'attendee_password_reset_requests',
            },
        ),
        migrations.CreateModel(
            name='AttendeeSubmitButton',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('hit_count', models.IntegerField()),
                ('attendee', models.ForeignKey(to='app.Attendee', null=True)),
            ],
            options={
                'db_table': 'attendee_submit_button',
            },
        ),
        migrations.CreateModel(
            name='AttendeeTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
            ],
            options={
                'db_table': 'attendee_tags',
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('check_in', models.DateField()),
                ('check_out', models.DateField()),
                ('broken_up', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
            ],
            options={
                'db_table': 'bookings',
            },
        ),
        migrations.CreateModel(
            name='Checkpoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('questions', models.TextField()),
                ('defaults', models.TextField(default=None, null=True)),
                ('allow_re_entry', models.BooleanField(default=False)),
                ('is_hide', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'checkpoints',
            },
        ),
        migrations.CreateModel(
            name='ContentPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('content', app.models.ContentType(choices=[('event', 'Event'), ('attendee', 'Attendee'), ('deleted_attendee', 'DeletedAttendee'), ('session', 'Session'), ('question', 'Question'), ('travel', 'Travel'), ('location', 'Location'), ('hotel', 'Hotel'), ('page', 'Page'), ('menu', 'Menu'), ('template', 'Template'), ('css', 'Css'), ('filter', 'Filter'), ('export_filter', 'ExportFilter'), ('photo_reel', 'PhotoReel'), ('message', 'Message'), ('file_browser', 'FileBrowser'), ('checkpoints', 'Checkpoints'), ('language', 'Language'), ('economy', 'Economy'), ('setting', 'Setting'), ('assign_session', 'AssignSession'), ('assign_travel', 'AssignTravel'), ('assign_hotel', 'AssignHotel'), ('group_registration', 'GroupRegistration')], max_length=20)),
                ('access_level', app.models.AccessLevel(choices=[('read', 'Read'), ('write', 'Write'), ('none', 'None')], default='none', max_length=10)),
                ('description', models.CharField(max_length=100, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'content_permissions',
            },
        ),
        migrations.CreateModel(
            name='Cookie',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('cookie_key', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'db_table': 'cookie',
            },
        ),
        migrations.CreateModel(
            name='CookiePage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('visit_count', models.IntegerField()),
                ('visit_date', models.DateField()),
                ('cookie', models.ForeignKey(to='app.Cookie')),
            ],
            options={
                'db_table': 'cookie_page',
            },
        ),
        migrations.CreateModel(
            name='CreditOrders',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('order_number', models.CharField(max_length=100)),
                ('cost_excluding_vat', models.FloatField()),
                ('cost_including_vat', models.FloatField(default=0)),
                ('type', app.models.OrderItemType(choices=[('session', 'Session'), ('hotel', 'Hotel'), ('travel', 'Travel'), ('rebate', 'Rebate'), ('adjustment', 'Adjustment')], max_length=100)),
                ('item_name', models.CharField(max_length=255)),
                ('status', app.models.OrderStatus(choices=[('open', 'Open'), ('pending', 'Pending'), ('paid', 'Paid'), ('cancelled', 'Cancelled')], default='open', max_length=100)),
                ('invoice_ref', models.CharField(max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'credit_orders',
            },
        ),
        migrations.CreateModel(
            name='CreditUsages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('order_number', models.CharField(max_length=100)),
                ('cost', models.FloatField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('credit_order', models.ForeignKey(to='app.CreditOrders')),
            ],
            options={
                'db_table': 'credit_usages',
            },
        ),
        migrations.CreateModel(
            name='CurrentEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
            ],
            options={
                'db_table': 'current_event',
            },
        ),
        migrations.CreateModel(
            name='CurrentFilter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('visible_columns', models.TextField(default=None, null=True)),
                ('show_rows', models.IntegerField(default=None, null=True)),
                ('table_type', models.CharField(default='attendee', max_length=100)),
                ('sorted_column', models.IntegerField(default=1, null=True)),
                ('sorting_order', models.CharField(default='asc', max_length=32)),
            ],
            options={
                'db_table': 'current_filter',
            },
        ),
        migrations.CreateModel(
            name='CustomClasses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('classname', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'custom_classes',
            },
        ),
        migrations.CreateModel(
            name='DashboardPlugin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('setting_data', models.TextField()),
                ('modified_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'dashboard_plugin',
            },
        ),
        migrations.CreateModel(
            name='DeletedAttendee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('firstname', models.CharField(max_length=50)),
                ('lastname', models.CharField(max_length=45)),
                ('email', models.CharField(max_length=45)),
                ('phonenumber', models.CharField(max_length=45)),
                ('deleted_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'deleted_attendees',
            },
        ),
        migrations.CreateModel(
            name='DeletedHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('activity_type', app.models.ActivityHistoryType(choices=[('update', 'Update'), ('delete', 'Delete'), ('register', 'Register'), ('message', 'Message'), ('offline', 'Offline Download'), ('check-in', 'Check In')], max_length=50)),
                ('category', app.models.ActivityCategoryType(choices=[('event', 'Event'), ('session', 'Session'), ('question', 'Question'), ('travel', 'Travel'), ('room', 'Room'), ('message', 'Message'), ('profile', 'Profile'), ('push_notification', 'Push_notification'), ('group', 'Group'), ('tag', 'Tag'), ('package', 'Package'), ('checkpoint', 'Checkpoint'), ('photo', 'Photo'), ('registration_group', 'Registration_group'), ('rebate', 'Rebate'), ('order', 'Order'), ('order_item', 'Order Item'), ('credit_order', 'Credit Order'), ('credit_usage', 'Credit Usage'), ('payment', 'Payment')], max_length=50)),
                ('old_value', models.TextField()),
                ('new_value', models.TextField()),
                ('created', models.DateTimeField()),
                ('activity_message', models.TextField(null=True)),
            ],
            options={
                'db_table': 'deleted_history',
            },
        ),
        migrations.CreateModel(
            name='DeviceToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('device_unique_id', models.CharField(max_length=255)),
                ('token', models.CharField(max_length=255)),
                ('os_type', app.models.OsType(choices=[('1', 'Android'), ('2', 'IOS')])),
                ('arn_enpoint', models.CharField(max_length=255)),
                ('is_enable', models.BooleanField(default=True)),
                ('offline_pakage_status', models.BooleanField(default=True)),
                ('package_download_count', models.IntegerField(default=0)),
                ('package_created_at', models.DateTimeField(null=True)),
                ('package_version', models.IntegerField(default=0)),
                ('attendee', models.ForeignKey(blank=True, to='app.Attendee', null=True)),
            ],
            options={
                'db_table': 'devices_token',
            },
        ),
        migrations.CreateModel(
            name='ElementDefaultLang',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('type', app.models.PluginType(choices=[('text', 'Text'), ('item_text', 'Item Text'), ('button', 'Button'), ('notification', 'Notification'), ('validation_text', 'Validation Text')], default='text', max_length=100)),
                ('lang_key', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=255)),
                ('default_value', models.TextField()),
            ],
            options={
                'db_table': 'element_default_lang',
            },
        ),
        migrations.CreateModel(
            name='ElementHtml',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('box_id', models.IntegerField()),
                ('compiled', models.TextField()),
                ('uncompiled', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'element_html',
            },
        ),
        migrations.CreateModel(
            name='ElementPresetLang',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('value', models.TextField()),
                ('element_default_lang', models.ForeignKey(to='app.ElementDefaultLang')),
            ],
            options={
                'db_table': 'element_preset_lang',
            },
        ),
        migrations.CreateModel(
            name='Elements',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.CharField(max_length=255)),
                ('type', app.models.ElementType(choices=[('plugin', 'Plugin'), ('public_notification', 'Public_notification'), ('default_plugin', 'Default_plugin')], default='plugin', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'elements',
            },
        ),
        migrations.CreateModel(
            name='ElementsAnswers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('answer', models.TextField()),
                ('description', models.TextField()),
                ('box_id', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'elements_answers',
            },
        ),
        migrations.CreateModel(
            name='ElementsQuestions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('question_key', models.CharField(max_length=1000)),
            ],
            options={
                'db_table': 'elements_questions',
            },
        ),
        migrations.CreateModel(
            name='EmailContents',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('subject', models.TextField()),
                ('subject_lang', models.TextField(default=None, null=True)),
                ('content', models.TextField()),
                ('name', models.CharField(max_length=255)),
                ('sender_email', models.CharField(default='mahedi@workspaceit.com', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_show', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'email_contents',
            },
        ),
        migrations.CreateModel(
            name='EmailLanguageContents',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('content', models.TextField()),
                ('email_content', models.ForeignKey(to='app.EmailContents')),
            ],
            options={
                'db_table': 'email_language_contents',
            },
        ),
        migrations.CreateModel(
            name='EmailReceivers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('firstname', models.CharField(max_length=255)),
                ('lastname', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('status', app.models.ReceiversStatus(choices=[('sent', 'Sent'), ('not_sent', 'Not_sent')], default='not_sent', max_length=100)),
                ('last_received', models.DateTimeField(auto_now=True)),
                ('is_show', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'email_receivers',
            },
        ),
        migrations.CreateModel(
            name='EmailReceiversHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('sending_at', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(to='app.EmailReceivers')),
            ],
            options={
                'db_table': 'email_receivers_history',
            },
        ),
        migrations.CreateModel(
            name='EmailTemplates',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('category', app.models.TemplateCategories(choices=[('web_pages', 'Web Pages'), ('email_templates', 'Email Templates'), ('invoices', 'Invoices'), ('pdf', 'Pdf')], max_length=25)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_show', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'email_templates',
            },
        ),
        migrations.CreateModel(
            name='EventAdmin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'event_admins',
            },
        ),
        migrations.CreateModel(
            name='Events',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=45)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('description', models.TextField()),
                ('url', models.CharField(max_length=50, null=True)),
                ('address', models.TextField(null=True)),
                ('is_show', models.BooleanField(default=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'events',
            },
        ),
        migrations.CreateModel(
            name='ExportNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('file_name', models.CharField(max_length=255, unique=True)),
                ('status', models.SmallIntegerField()),
                ('request_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'export_notification',
            },
        ),
        migrations.CreateModel(
            name='ExportRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('preset', models.TextField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('modified_at', models.DateField(auto_now=True)),
                ('export_order', models.IntegerField()),
            ],
            options={
                'db_table': 'export_rules',
            },
        ),
        migrations.CreateModel(
            name='ExportState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('file_name', models.CharField(max_length=255)),
                ('status', models.IntegerField(default=3, help_text='0=on progress, 1= found and done, 2=not found')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'export_state',
            },
        ),
        migrations.CreateModel(
            name='GeneralTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('category', app.models.TagType(choices=[('session', 'Session'), ('hotel', 'Hotel'), ('room', 'Room'), ('travel', 'Travel')], default='session', max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(default=11, to='app.Events')),
            ],
            options={
                'db_table': 'general_tags',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('name_lang', models.TextField(default=None, null=True)),
                ('type', app.models.GroupType(choices=[('attendee', 'Attendee'), ('session', 'Session'), ('hotel', 'Hotel'), ('filter', 'Filter'), ('payment', 'Payment'), ('question', 'Question'), ('location', 'Location'), ('travel', 'Travel'), ('export_filter', 'Export Filter'), ('menu', 'Menu'), ('email', 'Email')], max_length=50)),
                ('color', models.CharField(default=None, max_length=20, null=True)),
                ('group_order', models.IntegerField(default=1)),
                ('is_show', models.BooleanField(default=True)),
                ('is_searchable', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('event', models.ForeignKey(to='app.Events')),
            ],
            options={
                'db_table': 'groups',
            },
        ),
        migrations.CreateModel(
            name='GroupPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('access_level', app.models.AccessLevel(choices=[('read', 'Read'), ('write', 'Write'), ('none', 'None')], default='none', max_length=10)),
                ('description', models.CharField(max_length=100, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'group_permissions',
            },
        ),
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('name_lang', models.TextField(default=None, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('group', models.ForeignKey(to='app.Group')),
            ],
            options={
                'db_table': 'hotels',
            },
        ),
        migrations.CreateModel(
            name='ImportChangeRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('changed_data', models.TextField()),
                ('status', models.SmallIntegerField()),
                ('type', models.CharField(max_length=50, null=True)),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField(null=True)),
            ],
            options={
                'db_table': 'import_change_request',
            },
        ),
        migrations.CreateModel(
            name='ImportChangeStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('filename', models.TextField()),
                ('message', models.TextField(null=True)),
                ('duplicate_attendees', models.TextField(null=True)),
                ('status', models.SmallIntegerField()),
                ('import_change', models.ForeignKey(to='app.ImportChangeRequest', null=True)),
            ],
            options={
                'db_table': 'import_change_status',
            },
        ),
        migrations.CreateModel(
            name='Locations',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=45)),
                ('name_lang', models.TextField(default=None, null=True)),
                ('description', models.TextField(default=None, blank=True, null=True)),
                ('description_lang', models.TextField(default=None, null=True)),
                ('address', models.TextField(default=None, blank=True, null=True)),
                ('address_lang', models.TextField(default=None, null=True)),
                ('latitude', models.CharField(default=None, max_length=50, blank=True, null=True)),
                ('longitude', models.CharField(default=None, max_length=50, blank=True, null=True)),
                ('map_highlight', models.CharField(default=None, max_length=255, blank=True, null=True)),
                ('contact_name', models.CharField(default=None, max_length=255, blank=True, null=True)),
                ('contact_name_lang', models.TextField(default=None, null=True)),
                ('contact_web', models.TextField(default=None, blank=True, null=True)),
                ('contact_email', models.CharField(default=None, max_length=255, blank=True, null=True)),
                ('contact_phone', models.CharField(default=None, max_length=255, blank=True, null=True)),
                ('location_order', models.IntegerField()),
                ('show_map_highlight', models.BooleanField(default=False)),
                ('show_contact_name', models.BooleanField(default=False)),
                ('show_contact_web', models.BooleanField(default=False)),
                ('show_contact_email', models.BooleanField(default=False)),
                ('show_contact_phone', models.BooleanField(default=False)),
                ('group', models.ForeignKey(to='app.Group')),
            ],
            options={
                'db_table': 'locations',
            },
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('all_dates', models.CharField(default=None, max_length=1000)),
            ],
            options={
                'db_table': 'matches',
            },
        ),
        migrations.CreateModel(
            name='MatchLine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('booking', models.ForeignKey(to='app.Booking')),
                ('match', models.ForeignKey(related_name='lines', to='app.Match')),
            ],
            options={
                'db_table': 'match_line',
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=50)),
                ('title_lang', models.TextField(default=None, null=True)),
                ('url', models.CharField(max_length=255, null=True)),
                ('uid_include', models.BooleanField(default=False)),
                ('accept_login', models.BooleanField(default=False)),
                ('only_speaker', models.BooleanField(default=False)),
                ('level', models.IntegerField(default=0)),
                ('rank', models.IntegerField(default=0)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('is_visible', models.BooleanField(default=True)),
                ('available_offline', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('allow_unregistered', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'menu_items',
            },
        ),
        migrations.CreateModel(
            name='MenuPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('menu', models.ForeignKey(to='app.MenuItem')),
            ],
            options={
                'db_table': 'menu_permission',
            },
        ),
        migrations.CreateModel(
            name='MessageContents',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('sender_name', models.CharField(max_length=255)),
                ('type', app.models.MessageType(choices=[('push_or_sms', 'Push_or_Sms'), ('sms_and_push', 'Sms_and_Push'), ('sms', 'Sms'), ('push', 'Push'), ('plugin_message', 'Plugin_Message')], max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_show', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'message_contents',
            },
        ),
        migrations.CreateModel(
            name='MessageHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('subject', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('type', app.models.MessageHistoryType(choices=[('sms', 'SMS'), ('push', 'Push'), ('mail', 'Mail')], max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'message_history',
            },
        ),
        migrations.CreateModel(
            name='MessageLanguageContents',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('content', models.TextField()),
            ],
            options={
                'db_table': 'message_language_contents',
            },
        ),
        migrations.CreateModel(
            name='MessageReceivers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('firstname', models.CharField(max_length=255)),
                ('lastname', models.CharField(max_length=255)),
                ('mobile_phone', models.CharField(max_length=255)),
                ('status', app.models.ReceiversStatus(choices=[('sent', 'Sent'), ('not_sent', 'Not_sent')], default='not_sent', max_length=100)),
                ('last_received', models.DateTimeField(auto_now=True)),
                ('is_show', models.BooleanField(default=True)),
                ('push', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'message_receivers',
            },
        ),
        migrations.CreateModel(
            name='MessageReceiversHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('type', app.models.MessageHistoryType(choices=[('sms', 'SMS'), ('push', 'PUSH')], max_length=100)),
                ('sending_at', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(to='app.MessageReceivers')),
            ],
            options={
                'db_table': 'message_receivers_history',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('type', app.models.NotificationTypes(choices=[('session', 'Session'), ('admin', 'Admin'), ('attendee', 'Attendee'), ('group', 'Group'), ('session_attend', 'Session_attend'), ('filter_message', 'Filter_message')], max_length=100)),
                ('message', models.TextField()),
                ('status', models.BooleanField(default=False)),
                ('status_socket_message', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'notifications',
            },
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('option', models.CharField(max_length=255)),
                ('option_lang', models.TextField(default=None, null=True)),
                ('option_order', models.IntegerField(default=1)),
                ('default_value', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'options',
            },
        ),
        migrations.CreateModel(
            name='OrderItems',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('item_type', app.models.OrderItemType(choices=[('session', 'Session'), ('hotel', 'Hotel'), ('travel', 'Travel'), ('rebate', 'Rebate'), ('adjustment', 'Adjustment')], max_length=100)),
                ('item_id', models.IntegerField()),
                ('cost', models.FloatField(default=0)),
                ('rebate_amount', models.FloatField(default=0)),
                ('rebate_for_item_id', models.IntegerField(null=True)),
                ('vat_rate', models.FloatField(null=True)),
                ('rebate_for_item_type', app.models.OrderItemType(choices=[('session', 'Session'), ('hotel', 'Hotel'), ('travel', 'Travel'), ('rebate', 'Rebate'), ('adjustment', 'Adjustment')], max_length=100, null=True)),
                ('applied_on_open_order', models.BooleanField(default=True)),
                ('rebate_is_deleted', models.BooleanField(default=False)),
                ('item_booking_id', models.IntegerField(null=True)),
                ('effected_day_count', models.IntegerField(null=True)),
                ('booking_check_in', models.DateField(null=True)),
                ('booking_check_out', models.DateField(null=True)),
            ],
            options={
                'db_table': 'order_items',
            },
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('order_number', models.CharField(max_length=100)),
                ('cost', models.FloatField(default=0)),
                ('rebate_amount', models.FloatField(default=0)),
                ('vat_amount', models.FloatField(default=0)),
                ('due_date', models.DateTimeField(null=True)),
                ('status', app.models.OrderStatus(choices=[('open', 'Open'), ('pending', 'Pending'), ('paid', 'Paid'), ('cancelled', 'Cancelled')], default='open', max_length=100)),
                ('invoice_ref', models.CharField(max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('invoice_date', models.DateTimeField(default=None, null=True)),
                ('is_preselected', models.BooleanField(default=False)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
            ],
            options={
                'db_table': 'orders',
            },
        ),
        migrations.CreateModel(
            name='PageContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('url', models.CharField(max_length=255, null=True)),
                ('content', models.TextField()),
                ('login_required', models.BooleanField(default=False)),
                ('filter', models.TextField(default=None, null=True)),
                ('element_filter', models.TextField(default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_show', models.BooleanField(default=True)),
                ('disallow_logged_in', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'page_contents',
            },
        ),
        migrations.CreateModel(
            name='PageContentClasses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('box_id', models.IntegerField()),
                ('classname', models.ForeignKey(to='app.CustomClasses')),
                ('page', models.ForeignKey(to='app.PageContent')),
            ],
            options={
                'db_table': 'page_content_classes',
            },
        ),
        migrations.CreateModel(
            name='PageImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('path', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_shown', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'page_images',
            },
        ),
        migrations.CreateModel(
            name='PagePermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('page', models.ForeignKey(to='app.PageContent')),
            ],
            options={
                'db_table': 'page_permission',
            },
        ),
        migrations.CreateModel(
            name='PasswordResetRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('hash_code', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expired_at', models.DateTimeField(default=None)),
                ('already_used', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'password_reset_requests',
            },
        ),
        migrations.CreateModel(
            name='Payments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('order_number', models.CharField(default=0, max_length=100)),
                ('method', app.models.PaymentMethod(choices=[('dibs', 'Dibs'), ('admin', 'Admin')], max_length=100)),
                ('amount', models.FloatField()),
                ('details', models.TextField()),
                ('currency', models.CharField(max_length=32, null=True)),
                ('transaction', models.CharField(max_length=100, null=True)),
                ('invoice_ref', models.CharField(max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'payments',
            },
        ),
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
            ],
            options={
                'db_table': 'payment_settings',
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('photo', models.CharField(max_length=1000)),
                ('is_approved', models.IntegerField(default=0)),
                ('thumb_image', models.CharField(max_length=1000, null=True)),
                ('comment', models.TextField(null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
            ],
            options={
                'db_table': 'photos',
            },
        ),
        migrations.CreateModel(
            name='PhotoGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'photo_group',
            },
        ),
        migrations.CreateModel(
            name='PluginPdfButton',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'plugin_pdf_button',
            },
        ),
        migrations.CreateModel(
            name='PluginSubmitButton',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'plugin_submit_button',
            },
        ),
        migrations.CreateModel(
            name='PresetEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('event', models.ForeignKey(to='app.Events')),
            ],
            options={
                'db_table': 'preset_event',
            },
        ),
        migrations.CreateModel(
            name='Presets',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('preset_name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('language_code', models.CharField(default='en', max_length=10)),
                ('date_format', models.CharField(default='Y-m-d', max_length=50)),
                ('time_format', models.CharField(default='H:i', max_length=50)),
                ('datetime_format', models.CharField(default='Y-m-d H:i', max_length=50)),
                ('datetime_language', models.TextField(default=None, null=True)),
            ],
            options={
                'db_table': 'presets',
            },
        ),
        migrations.CreateModel(
            name='QuestionPreRequisite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('action', models.BooleanField(default=True)),
                ('pre_req_answer', models.ForeignKey(to='app.Option')),
            ],
            options={
                'db_table': 'question_pre_requisite',
            },
        ),
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=255)),
                ('title_lang', models.TextField(default=None, null=True)),
                ('type', models.CharField(max_length=255)),
                ('description', models.TextField(default=None, null=True)),
                ('description_lang', models.TextField(default=None, null=True)),
                ('min_character', models.IntegerField(null=True)),
                ('max_character', models.IntegerField(null=True)),
                ('regular_expression', models.TextField(default=None, null=True)),
                ('default_answer', models.TextField(default=None, null=True)),
                ('default_answer_status', app.models.DefaultAnswerStatus(choices=[('set', 'Set Value'), ('leave', 'Leave as is'), ('empty', 'Empty Value')], default='leave', max_length=50)),
                ('question_class', models.CharField(max_length=255, null=True)),
                ('required', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('question_order', models.IntegerField()),
                ('actual_definition', models.CharField(max_length=50, null=True)),
                ('show_description', models.BooleanField(default=False)),
                ('from_date', models.DateField(default=None, blank=True, null=True)),
                ('to_date', models.DateField(default=None, blank=True, null=True)),
                ('from_time', models.TimeField(default=None, blank=True, null=True)),
                ('to_time', models.TimeField(default=None, blank=True, null=True)),
                ('time_interval', models.CharField(max_length=2, null=True)),
                ('group', models.ForeignKey(to='app.Group')),
            ],
            options={
                'db_table': 'questions',
            },
        ),
        migrations.CreateModel(
            name='Rebates',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('type_id', models.TextField(default=None, null=True)),
                ('rebate_type', app.models.RebateType(choices=[('percentage', 'Percentage'), ('fixed', 'Fixed sum')], max_length=100)),
                ('value', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'rebates',
            },
        ),
        migrations.CreateModel(
            name='RegistrationGroupOwner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
            ],
            options={
                'db_table': 'registration_group_owner',
            },
        ),
        migrations.CreateModel(
            name='RegistrationGroups',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=256)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_show', models.BooleanField(default=True)),
                ('event', models.ForeignKey(to='app.Events')),
            ],
            options={
                'db_table': 'registration_groups',
            },
        ),
        migrations.CreateModel(
            name='RequestedBuddy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('exists', models.BooleanField(default=True)),
                ('email', models.CharField(max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('booking', models.ForeignKey(related_name='buddies', to='app.Booking')),
                ('buddy', models.ForeignKey(to='app.Attendee', null=True)),
            ],
            options={
                'db_table': 'requested_buddies',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('description', models.CharField(max_length=255)),
                ('description_lang', models.TextField(default=None, null=True)),
                ('cost', models.FloatField(default=0, null=True)),
                ('beds', models.IntegerField()),
                ('vat', models.FloatField(null=True)),
                ('room_order', models.IntegerField()),
                ('keep_hotel', models.BooleanField(default=True)),
                ('pay_whole_amount', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('hotel', models.ForeignKey(to='app.Hotel')),
            ],
            options={
                'db_table': 'rooms',
            },
        ),
        migrations.CreateModel(
            name='RoomAllotment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('allotments', models.IntegerField()),
                ('available_date', models.DateField()),
                ('cost', models.FloatField(default=0, null=True)),
                ('vat', models.FloatField(null=True)),
                ('room', models.ForeignKey(to='app.Room')),
            ],
            options={
                'db_table': 'room_allotments',
            },
        ),
        migrations.CreateModel(
            name='RuleSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('preset', models.TextField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('modified_at', models.DateField(auto_now=True)),
                ('rule_order', models.IntegerField()),
                ('is_limit', models.BooleanField(default=False)),
                ('limit_amount', models.IntegerField(default=0)),
                ('matchfor', models.CharField(max_length=1, null=True)),
            ],
            options={
                'db_table': 'rule_set',
            },
        ),
        migrations.CreateModel(
            name='Scan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('status', models.SmallIntegerField(default=0)),
                ('scan_time', models.DateTimeField(auto_now_add=True)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
                ('checkpoint', models.ForeignKey(to='app.Checkpoint', null=True, default=None)),
            ],
            options={
                'db_table': 'scans',
            },
        ),
        migrations.CreateModel(
            name='Seminars',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=45)),
                ('date', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'seminars',
            },
        ),
        migrations.CreateModel(
            name='SeminarSpeakers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'seminars_has_speakers',
            },
        ),
        migrations.CreateModel(
            name='SeminarsUsers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('status', app.models.AttendeeSessionStatus(choices=[('attending', 'Attending'), ('in-queue', 'In Cue'), ('not-attending', 'Not Attending'), ('deciding', 'Deciding')], default='attending', max_length=20)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('queue_order', models.IntegerField(default=1)),
                ('status_socket_nextup', models.BooleanField(default=False)),
                ('status_socket_evaluation', models.BooleanField(default=False)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
            ],
            options={
                'db_table': 'seminars_has_users',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('name_lang', models.TextField(default=None, null=True)),
                ('description', models.TextField()),
                ('description_lang', models.TextField(default=None, null=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('reg_between_start', models.DateField()),
                ('reg_between_end', models.DateField()),
                ('max_attendees', models.IntegerField(default=None, null=True)),
                ('allow_attendees_queue', models.BooleanField(default=False)),
                ('speakers', models.CharField(default=None, max_length=1024, null=True)),
                ('has_time', models.BooleanField(default=True)),
                ('receive_answer', models.BooleanField(default=False)),
                ('show_on_evaluation', models.BooleanField(default=True)),
                ('show_on_next_up', models.BooleanField(default=True)),
                ('allow_overlapping', models.BooleanField(default=False)),
                ('all_day', models.BooleanField(default=False)),
                ('session_order', models.IntegerField()),
                ('default_answer', app.models.AttendeeSessionStatus(choices=[('attending', 'Attending'), ('in-queue', 'In Cue'), ('not-attending', 'Not Attending'), ('deciding', 'Deciding')], default='attending', max_length=20)),
                ('default_answer_status', app.models.DefaultAnswerStatus(choices=[('set', 'Set Value'), ('leave', 'Leave as is'), ('empty', 'Empty Value')], default='leave', max_length=50)),
                ('cost', models.FloatField(default=0, null=True)),
                ('vat', models.FloatField(null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('group', models.ForeignKey(to='app.Group')),
                ('location', models.ForeignKey(to='app.Locations')),
            ],
            options={
                'db_table': 'sessions',
            },
        ),
        migrations.CreateModel(
            name='SessionClasses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('classname', models.ForeignKey(to='app.CustomClasses')),
                ('session', models.ForeignKey(to='app.Session')),
            ],
            options={
                'db_table': 'session_has_classes',
            },
        ),
        migrations.CreateModel(
            name='SessionRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('rating', models.IntegerField()),
                ('attendee', models.ForeignKey(to='app.Attendee')),
                ('session', models.ForeignKey(to='app.Session')),
            ],
            options={
                'db_table': 'session_ratings',
            },
        ),
        migrations.CreateModel(
            name='SessionTags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('session', models.ForeignKey(to='app.Session')),
                ('tag', models.ForeignKey(to='app.GeneralTag')),
            ],
            options={
                'db_table': 'session_has_tags',
            },
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=500)),
                ('event', models.ForeignKey(to='app.Events')),
            ],
            options={
                'db_table': 'settings',
            },
        ),
        migrations.CreateModel(
            name='StyleSheet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('style', models.TextField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('version', models.IntegerField(default=1)),
            ],
            options={
                'db_table': 'event_stylesheets',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('event', models.ForeignKey(default=10, to='app.Events')),
            ],
            options={
                'db_table': 'tags',
            },
        ),
        migrations.CreateModel(
            name='Travel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('name_lang', models.TextField(default=None, null=True)),
                ('description', models.TextField()),
                ('description_lang', models.TextField(default=None, null=True)),
                ('departure_city', models.CharField(max_length=255)),
                ('arrival_city', models.CharField(max_length=255)),
                ('departure', models.DateTimeField()),
                ('arrival', models.DateTimeField()),
                ('reg_between_start', models.DateField()),
                ('reg_between_end', models.DateField()),
                ('travel_bound', app.models.TravelBound(choices=[('homebound', 'HomeBound'), ('outbound', 'OutBound')], max_length=20)),
                ('max_attendees', models.IntegerField()),
                ('allow_attendees_queue', models.BooleanField(default=False)),
                ('travel_order', models.IntegerField()),
                ('default_answer', app.models.AttendeeSessionStatus(choices=[('attending', 'Attending'), ('in-queue', 'In Cue'), ('not-attending', 'Not Attending'), ('deciding', 'Deciding')], default='attending', max_length=20)),
                ('default_answer_status', app.models.DefaultAnswerStatus(choices=[('set', 'Set Value'), ('leave', 'Leave as is'), ('empty', 'Empty Value')], default='leave', max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('group', models.ForeignKey(to='app.Group')),
                ('location', models.ForeignKey(to='app.Locations')),
            ],
            options={
                'db_table': 'travels',
            },
        ),
        migrations.CreateModel(
            name='TravelAttendee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('status', app.models.AttendeeSessionStatus(choices=[('attending', 'Attending'), ('in-queue', 'In Cue'), ('not-attending', 'Not Attending'), ('deciding', 'Deciding')], default='attending', max_length=20)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('queue_order', models.IntegerField(default=1)),
                ('attendee', models.ForeignKey(to='app.Attendee')),
                ('travel', models.ForeignKey(to='app.Travel')),
            ],
            options={
                'db_table': 'travel_has_attendees',
            },
        ),
        migrations.CreateModel(
            name='TravelBoundRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('travel_homebound', models.ForeignKey(related_name='travel_homebound', to='app.Travel')),
                ('travel_outbound', models.ForeignKey(related_name='travel_outbound', to='app.Travel')),
            ],
            options={
                'db_table': 'travel_bound_relation',
            },
        ),
        migrations.CreateModel(
            name='TravelTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('tag', models.ForeignKey(to='app.GeneralTag')),
                ('travel', models.ForeignKey(to='app.Travel')),
            ],
            options={
                'db_table': 'travel_has_tags',
            },
        ),
        migrations.CreateModel(
            name='UsedRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('rule', models.ForeignKey(related_name='rules', to='app.RuleSet')),
            ],
            options={
                'db_table': 'used_rule',
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('firstname', models.CharField(max_length=45)),
                ('lastname', models.CharField(max_length=45)),
                ('company', models.CharField(max_length=45)),
                ('email', models.CharField(max_length=45)),
                ('password', models.CharField(max_length=150)),
                ('phonenumber', models.CharField(max_length=45)),
                ('role', app.models.UserRoles(choices=[('student', 'Student'), ('participant', 'Participant'), ('speaker', 'Speaker'), ('vip', 'Vip')], default='vip', max_length=20)),
                ('type', app.models.UserTypes(choices=[('super_admin', 'SuperAdmin'), ('admin', 'Admin'), ('third_party_admin', 'ThirdPartyAdmin')], max_length=50)),
                ('status', app.models.UserStatus(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='VisibleColumns',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('visible_columns', models.TextField(default=None, null=True)),
                ('type', app.models.ColumnType(choices=[('session', 'Session'), ('hotel', 'Hotel')], max_length=50)),
                ('admin', models.ForeignKey(to='app.Users')),
                ('event', models.ForeignKey(to='app.Events')),
            ],
            options={
                'db_table': 'visible_columns',
            },
        ),
        migrations.AddField(
            model_name='usedrule',
            name='user',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='stylesheet',
            name='created_by',
            field=models.ForeignKey(default=None, to='app.Users'),
        ),
        migrations.AddField(
            model_name='stylesheet',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='seminarsusers',
            name='session',
            field=models.ForeignKey(to='app.Session'),
        ),
        migrations.AddField(
            model_name='seminarspeakers',
            name='session',
            field=models.ForeignKey(to='app.Session'),
        ),
        migrations.AddField(
            model_name='seminarspeakers',
            name='speaker',
            field=models.ForeignKey(to='app.Attendee'),
        ),
        migrations.AddField(
            model_name='ruleset',
            name='created_by',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='ruleset',
            name='group',
            field=models.ForeignKey(to='app.Group'),
        ),
        migrations.AddField(
            model_name='registrationgroupowner',
            name='group',
            field=models.ForeignKey(to='app.RegistrationGroups'),
        ),
        migrations.AddField(
            model_name='registrationgroupowner',
            name='owner',
            field=models.ForeignKey(to='app.Attendee'),
        ),
        migrations.AddField(
            model_name='rebates',
            name='created_by',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='rebates',
            name='event',
            field=models.ForeignKey(to='app.Events', null=True),
        ),
        migrations.AddField(
            model_name='questionprerequisite',
            name='pre_req_question',
            field=models.ForeignKey(related_name='pre_req_question', to='app.Questions'),
        ),
        migrations.AddField(
            model_name='questionprerequisite',
            name='question',
            field=models.ForeignKey(related_name='question', to='app.Questions'),
        ),
        migrations.AddField(
            model_name='presets',
            name='created_by',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='presets',
            name='event',
            field=models.ForeignKey(to='app.Events', null=True),
        ),
        migrations.AddField(
            model_name='presetevent',
            name='preset',
            field=models.ForeignKey(to='app.Presets'),
        ),
        migrations.AddField(
            model_name='pluginsubmitbutton',
            name='created_by',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='pluginsubmitbutton',
            name='page',
            field=models.ForeignKey(to='app.PageContent'),
        ),
        migrations.AddField(
            model_name='pluginpdfbutton',
            name='created_by',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='pluginpdfbutton',
            name='page',
            field=models.ForeignKey(to='app.PageContent'),
        ),
        migrations.AddField(
            model_name='photogroup',
            name='created_by',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='photogroup',
            name='page',
            field=models.ForeignKey(to='app.PageContent'),
        ),
        migrations.AddField(
            model_name='photo',
            name='group',
            field=models.ForeignKey(to='app.PhotoGroup', null=True),
        ),
        migrations.AddField(
            model_name='paymentsettings',
            name='created_by',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='paymentsettings',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='payments',
            name='created_by',
            field=models.ForeignKey(to='app.Users', null=True),
        ),
        migrations.AddField(
            model_name='passwordresetrequest',
            name='user',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='pagepermission',
            name='rule',
            field=models.ForeignKey(to='app.RuleSet', null=True, default=None),
        ),
        migrations.AddField(
            model_name='pageimage',
            name='created_by',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='pageimage',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='pageimage',
            name='page',
            field=models.ForeignKey(default=None, to='app.PageContent'),
        ),
        migrations.AddField(
            model_name='pagecontent',
            name='created_by',
            field=models.ForeignKey(related_name='created_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='pagecontent',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='pagecontent',
            name='last_updated_by',
            field=models.ForeignKey(related_name='last_updated_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='pagecontent',
            name='template',
            field=models.ForeignKey(to='app.EmailTemplates'),
        ),
        migrations.AddField(
            model_name='orders',
            name='created_by',
            field=models.ForeignKey(to='app.Users', null=True),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='order',
            field=models.ForeignKey(to='app.Orders'),
        ),
        migrations.AddField(
            model_name='orderitems',
            name='rebate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='app.Rebates', null=True),
        ),
        migrations.AddField(
            model_name='option',
            name='question',
            field=models.ForeignKey(to='app.Questions'),
        ),
        migrations.AddField(
            model_name='notification',
            name='clash_session',
            field=models.ForeignKey(to='app.Session', related_name='notification_clash_session', null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='message_content',
            field=models.ForeignKey(to='app.MessageContents', null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='new_session',
            field=models.ForeignKey(to='app.Session', related_name='notification_new_session', null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='sender_attendee',
            field=models.ForeignKey(to='app.Attendee', related_name='notification_sender_attendee', null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='to_attendee',
            field=models.ForeignKey(related_name='notification_to_attendee', to='app.Attendee'),
        ),
        migrations.AddField(
            model_name='messagereceivers',
            name='added_by',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='messagereceivers',
            name='attendee',
            field=models.ForeignKey(to='app.Attendee', null=True),
        ),
        migrations.AddField(
            model_name='messagereceivers',
            name='message_content',
            field=models.ForeignKey(to='app.MessageContents'),
        ),
        migrations.AddField(
            model_name='messagelanguagecontents',
            name='language',
            field=models.ForeignKey(to='app.Presets'),
        ),
        migrations.AddField(
            model_name='messagelanguagecontents',
            name='message_content',
            field=models.ForeignKey(to='app.MessageContents'),
        ),
        migrations.AddField(
            model_name='messagehistory',
            name='admin',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='messagecontents',
            name='created_by',
            field=models.ForeignKey(related_name='message_created_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='messagecontents',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='messagecontents',
            name='last_updated_by',
            field=models.ForeignKey(related_name='message_last_updated_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='menupermission',
            name='rule',
            field=models.ForeignKey(to='app.RuleSet', null=True, default=None),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='content',
            field=models.ForeignKey(blank=True, to='app.PageContent', null=True),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='created_by',
            field=models.ForeignKey(related_name='menu_created_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='event',
            field=models.ForeignKey(to='app.Events', null=True, default=None),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='last_updated_by',
            field=models.ForeignKey(related_name='menu_last_updated_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='parent',
            field=models.ForeignKey(blank=True, to='app.MenuItem', null=True),
        ),
        migrations.AddField(
            model_name='match',
            name='room',
            field=models.ForeignKey(to='app.Room'),
        ),
        migrations.AddField(
            model_name='importchangerequest',
            name='approved_by',
            field=models.ForeignKey(to='app.Users', related_name='approved_by', null=True),
        ),
        migrations.AddField(
            model_name='importchangerequest',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='importchangerequest',
            name='imported_by',
            field=models.ForeignKey(related_name='imported_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='hotel',
            name='location',
            field=models.ForeignKey(to='app.Locations'),
        ),
        migrations.AddField(
            model_name='grouppermission',
            name='admin',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='grouppermission',
            name='group',
            field=models.ForeignKey(to='app.Group'),
        ),
        migrations.AddField(
            model_name='exportstate',
            name='admin',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='exportstate',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='exportrule',
            name='created_by',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='exportrule',
            name='group',
            field=models.ForeignKey(to='app.Group'),
        ),
        migrations.AddField(
            model_name='exportnotification',
            name='admin',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='exportnotification',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='events',
            name='admin',
            field=models.ForeignKey(to='app.Users', null=True),
        ),
        migrations.AddField(
            model_name='events',
            name='created_by',
            field=models.ForeignKey(related_name='created_by_event', to='app.Users'),
        ),
        migrations.AddField(
            model_name='events',
            name='last_updated_by',
            field=models.ForeignKey(related_name='last_updated_by_event', to='app.Users'),
        ),
        migrations.AddField(
            model_name='eventadmin',
            name='admin',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='eventadmin',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='emailtemplates',
            name='created_by',
            field=models.ForeignKey(related_name='template_created_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='emailtemplates',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='emailtemplates',
            name='last_updated_by',
            field=models.ForeignKey(related_name='template_last_updated_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='emailreceivers',
            name='added_by',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='emailreceivers',
            name='attendee',
            field=models.ForeignKey(to='app.Attendee', null=True),
        ),
        migrations.AddField(
            model_name='emailreceivers',
            name='email_content',
            field=models.ForeignKey(to='app.EmailContents'),
        ),
        migrations.AddField(
            model_name='emaillanguagecontents',
            name='language',
            field=models.ForeignKey(to='app.Presets'),
        ),
        migrations.AddField(
            model_name='emailcontents',
            name='created_by',
            field=models.ForeignKey(related_name='content_created_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='emailcontents',
            name='last_updated_by',
            field=models.ForeignKey(related_name='content_last_updated_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='emailcontents',
            name='template',
            field=models.ForeignKey(to='app.EmailTemplates'),
        ),
        migrations.AddField(
            model_name='elementsquestions',
            name='created_by',
            field=models.ForeignKey(related_name='element_question_created_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='elementsquestions',
            name='group',
            field=models.ForeignKey(to='app.Elements'),
        ),
        migrations.AddField(
            model_name='elementsquestions',
            name='last_updated_by',
            field=models.ForeignKey(related_name='element_question_last_updated_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='elementsanswers',
            name='created_by',
            field=models.ForeignKey(related_name='element_answer_created_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='elementsanswers',
            name='element_question',
            field=models.ForeignKey(to='app.ElementsQuestions'),
        ),
        migrations.AddField(
            model_name='elementsanswers',
            name='last_updated_by',
            field=models.ForeignKey(related_name='element_answer_last_updated_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='elementsanswers',
            name='page',
            field=models.ForeignKey(to='app.PageContent'),
        ),
        migrations.AddField(
            model_name='elements',
            name='created_by',
            field=models.ForeignKey(related_name='element_created_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='elements',
            name='last_updated_by',
            field=models.ForeignKey(related_name='element_last_updated_by', to='app.Users'),
        ),
        migrations.AddField(
            model_name='elementpresetlang',
            name='preset',
            field=models.ForeignKey(to='app.Presets'),
        ),
        migrations.AddField(
            model_name='elementhtml',
            name='created_by',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='elementhtml',
            name='language',
            field=models.ForeignKey(to='app.Presets', null=True),
        ),
        migrations.AddField(
            model_name='elementhtml',
            name='page',
            field=models.ForeignKey(to='app.PageContent'),
        ),
        migrations.AddField(
            model_name='elementdefaultlang',
            name='element',
            field=models.ForeignKey(to='app.Elements'),
        ),
        migrations.AddField(
            model_name='deletedhistory',
            name='admin',
            field=models.ForeignKey(to='app.Users', null=True),
        ),
        migrations.AddField(
            model_name='deletedhistory',
            name='attendee',
            field=models.ForeignKey(to='app.DeletedAttendee'),
        ),
        migrations.AddField(
            model_name='deletedhistory',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='deletedhistory',
            name='message',
            field=models.ForeignKey(to='app.MessageHistory', null=True),
        ),
        migrations.AddField(
            model_name='deletedhistory',
            name='photo',
            field=models.ForeignKey(to='app.Photo', null=True),
        ),
        migrations.AddField(
            model_name='deletedhistory',
            name='question',
            field=models.ForeignKey(to='app.Questions', null=True),
        ),
        migrations.AddField(
            model_name='deletedhistory',
            name='registration_group',
            field=models.ForeignKey(to='app.RegistrationGroups', null=True),
        ),
        migrations.AddField(
            model_name='deletedhistory',
            name='room',
            field=models.ForeignKey(to='app.Room', null=True),
        ),
        migrations.AddField(
            model_name='deletedhistory',
            name='session',
            field=models.ForeignKey(to='app.Session', null=True),
        ),
        migrations.AddField(
            model_name='deletedhistory',
            name='travel',
            field=models.ForeignKey(to='app.Travel', null=True),
        ),
        migrations.AddField(
            model_name='deletedattendee',
            name='deleted_by',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='deletedattendee',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='dashboardplugin',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='dashboardplugin',
            name='modified_by',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='customclasses',
            name='created_by',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='customclasses',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='currentfilter',
            name='admin',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='currentfilter',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='currentfilter',
            name='filter',
            field=models.ForeignKey(to='app.RuleSet', null=True, default=None),
        ),
        migrations.AddField(
            model_name='currentevent',
            name='admin',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='currentevent',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='creditorders',
            name='created_by',
            field=models.ForeignKey(to='app.Users', null=True),
        ),
        migrations.AddField(
            model_name='creditorders',
            name='order',
            field=models.ForeignKey(to='app.Orders'),
        ),
        migrations.AddField(
            model_name='cookiepage',
            name='page',
            field=models.ForeignKey(to='app.PageContent'),
        ),
        migrations.AddField(
            model_name='contentpermission',
            name='admin',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='contentpermission',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='checkpoint',
            name='created_by',
            field=models.ForeignKey(to='app.Users'),
        ),
        migrations.AddField(
            model_name='checkpoint',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='checkpoint',
            name='filter',
            field=models.ForeignKey(to='app.RuleSet', null=True),
        ),
        migrations.AddField(
            model_name='checkpoint',
            name='session',
            field=models.ForeignKey(to='app.Session', null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='room',
            field=models.ForeignKey(to='app.Room'),
        ),
        migrations.AddField(
            model_name='attendeetag',
            name='tag',
            field=models.ForeignKey(to='app.Tag'),
        ),
        migrations.AddField(
            model_name='attendeesubmitbutton',
            name='button',
            field=models.ForeignKey(to='app.PluginSubmitButton'),
        ),
        migrations.AddField(
            model_name='attendeegroups',
            name='group',
            field=models.ForeignKey(to='app.Group'),
        ),
        migrations.AddField(
            model_name='attendee',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='attendee',
            name='language',
            field=models.ForeignKey(to='app.Presets'),
        ),
        migrations.AddField(
            model_name='attendee',
            name='registration_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='app.RegistrationGroups', null=True),
        ),
        migrations.AddField(
            model_name='answers',
            name='question',
            field=models.ForeignKey(to='app.Questions'),
        ),
        migrations.AddField(
            model_name='answers',
            name='user',
            field=models.ForeignKey(to='app.Attendee'),
        ),
        migrations.AddField(
            model_name='activityhistory',
            name='admin',
            field=models.ForeignKey(to='app.Users', null=True),
        ),
        migrations.AddField(
            model_name='activityhistory',
            name='attendee',
            field=models.ForeignKey(to='app.Attendee'),
        ),
        migrations.AddField(
            model_name='activityhistory',
            name='checkpoint',
            field=models.ForeignKey(to='app.Checkpoint', null=True),
        ),
        migrations.AddField(
            model_name='activityhistory',
            name='event',
            field=models.ForeignKey(to='app.Events'),
        ),
        migrations.AddField(
            model_name='activityhistory',
            name='message',
            field=models.ForeignKey(to='app.MessageHistory', null=True),
        ),
        migrations.AddField(
            model_name='activityhistory',
            name='photo',
            field=models.ForeignKey(to='app.Photo', null=True),
        ),
        migrations.AddField(
            model_name='activityhistory',
            name='question',
            field=models.ForeignKey(to='app.Questions', null=True),
        ),
        migrations.AddField(
            model_name='activityhistory',
            name='registration_group',
            field=models.ForeignKey(to='app.RegistrationGroups', null=True),
        ),
        migrations.AddField(
            model_name='activityhistory',
            name='room',
            field=models.ForeignKey(to='app.Room', null=True),
        ),
        migrations.AddField(
            model_name='activityhistory',
            name='session',
            field=models.ForeignKey(to='app.Session', null=True),
        ),
        migrations.AddField(
            model_name='activityhistory',
            name='travel',
            field=models.ForeignKey(to='app.Travel', null=True),
        ),
    ]
