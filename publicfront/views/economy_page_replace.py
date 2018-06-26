from django.views import generic
import re
from django.template.loader import render_to_string

from app.models import Orders
from publicfront.views.lang_key import LanguageKey
from app.views.gbhelper.error_report_helper import ErrorR
from app.views.gbhelper.economy_library import  EconomyLibrary

class EconomyPageReplace(generic.View):
    def replace_order_owner(request, pageContents):
        ErrorR.ex_time_init()
        try:
            content = ''
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                order_owner_regex = r"({order_owner})"
                order_owner_matches = re.findall(order_owner_regex, pageContents)
                if len(order_owner_matches) > 0:
                    context = {}
                    user_id = request.session['event_user']['id']
                    order_owner = ''
                    orders = Orders.objects.filter(attendee_id=user_id).exclude(status='cancelled')
                    if orders.exists():
                        if orders[0].attendee.registration_group:
                            owner = orders[0].attendee.registration_group.registrationgroupowner_set.get().owner
                            order_owner = owner.firstname + ' ' + owner.lastname
                        else:
                            order_owner = orders[0].attendee.firstname + ' ' + orders[0].attendee.lastname
                        content = order_owner
                    else:
                        content = ''
                else:
                    content = ''
            else:
                content = ''
        except Exception as e:
            ErrorR.efail(e)
            content = ''
        pageContents = pageContents.replace('{order_owner}', content)
        ErrorR.ex_time()
        return pageContents

    def replace_order_table(request, pageContents):
        try:
            content = ''
            base_url = request.session['base_url']
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                event_id = request.session['event_id']
                order_table_regex = r"({order_table})"
                oder_table_matches = re.findall(order_table_regex, pageContents)
                print(oder_table_matches)
                if len(oder_table_matches)>0:
                    context={}
                    user_id =request.session['event_user']['id']

                    economy_data = EconomyLibrary.get_order_tables(user_id, event_id, True)
                    if economy_data['order_type'] == 'attendee-order':
                        orders = economy_data['order_list']
                    else:
                        orders = []

                    language = LanguageKey.catch_lang_key_obj(request,'economy')
                    context['language'] = language
                    context['orders'] = orders
                    context['order_table_type'] = 'attendee-order'
                    content = render_to_string('public/tags/order_table_tag.html',context)

                else:
                    content=''
            else:
               content=''



        except Exception as e:
            ErrorR.efail(e)
            content=''

        pageContents = pageContents.replace('{order_table}', content)
        return pageContents

    def replace_multiple_order_table(request, pageContents):
        try:
            content = ''
            base_url = request.session['base_url']
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                event_id = request.session['event_id']
                order_table_regex = r"({multiple_order_table})"
                oder_table_matches = re.findall(order_table_regex, pageContents)
                if len(oder_table_matches) > 0:
                    context = {}
                    user_id = request.session['event_user']['id']

                    economy_data = EconomyLibrary.get_order_tables(user_id, event_id, True)
                    if economy_data['order_type'] == 'group-order':
                        orders = economy_data['order_list']
                    else:
                        orders = []

                    language = LanguageKey.catch_lang_key_obj(request, 'economy')
                    context['language'] = language
                    context['orders'] = orders
                    # context['order_table_type'] = 'attendee-order'
                    content = render_to_string('public/tags/order_table_tag.html', context)

                else:
                    content = ''
            else:
                content = ''



        except Exception as e:
            ErrorR.efail(e)
            content = ''

        pageContents = pageContents.replace('{multiple_order_table}', content)
        return pageContents

    def replace_balance_table(request, pageContents):
        try:
            content = ''
            base_url = request.session['base_url']
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:
                event_id = request.session['event_id']
                order_table_regex = r"({balance_table})"
                oder_table_matches = re.findall(order_table_regex, pageContents)
                if len(oder_table_matches) > 0:
                    context = {}
                    user_id = request.session['event_user']['id']
                    balance_tables = EconomyLibrary.get_balance_tables(user_id, event_id)
                    language = LanguageKey.catch_lang_key_obj(request, 'economy')
                    context['language'] = language
                    context['balance_tables'] = balance_tables
                    context['download'] = True
                    # context['order_table_type'] = 'attendee-order'
                    content = render_to_string('public/tags/balance_table_tag.html', context)

                else:
                    content = ''
            else:
                content = ''



        except Exception as e:
            ErrorR.efail(e)
            content = ''

        pageContents = pageContents.replace('{balance_table}', content)
        return pageContents


    def replace_order_value_paid_order(request, pageContents):
        try:
            content = ''
            base_url = request.session['base_url']
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:

                order_table_regex = r"({order_value_paid_order})"
                oder_table_matches = re.findall(order_table_regex, pageContents)
                if len(oder_table_matches) > 0:
                    context = {}
                    user_id = request.session['event_user']['id']
                    value = EconomyLibrary.get_order_value(user_id,'paid')
                    if value is not None:
                        content = str(value)
                    else:
                        content = str(0)
                    # language = LanguageKey.catch_lang_key_obj(request, 'economy')
                    # context['language'] = language
                    # context['balance_tables'] = balance_tables
                    # # context['order_table_type'] = 'attendee-order'
                    # content = render_to_string('public/tags/balance_table_tag.html', context)

                else:
                    content = ''
            else:
                content = ''



        except Exception as e:
            ErrorR.efail(e)
            content = ''

        pageContents = pageContents.replace('{order_value_paid_order}', content)
        return pageContents

    def replace_multiple_order_value_paid_order(request, pageContents):
        try:
            content = ''
            base_url = request.session['base_url']
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:

                order_table_regex = r"({multiple_order_value_paid_order})"
                oder_table_matches = re.findall(order_table_regex, pageContents)
                if len(oder_table_matches) > 0:
                    context = {}
                    user_id = request.session['event_user']['id']
                    value = EconomyLibrary.get_order_value(user_id,'paid','group-order')
                    if value is not None:
                        content = str(value)
                    else:
                        content = str(0)
                    # language = LanguageKey.catch_lang_key_obj(request, 'economy')
                    # context['language'] = language
                    # context['balance_tables'] = balance_tables
                    # # context['order_table_type'] = 'attendee-order'
                    # content = render_to_string('public/tags/balance_table_tag.html', context)

                else:
                    content = ''
            else:
                content = ''



        except Exception as e:
            ErrorR.efail(e)
            content = ''

        pageContents = pageContents.replace('{multiple_order_value_paid_order}', content)
        return pageContents

    def replace_order_value_pending_order(request, pageContents):
        try:
            content = ''
            base_url = request.session['base_url']
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:

                order_table_regex = r"({order_value_pending_order})"
                oder_table_matches = re.findall(order_table_regex, pageContents)
                if len(oder_table_matches) > 0:
                    context = {}
                    user_id = request.session['event_user']['id']
                    value = EconomyLibrary.get_order_value(user_id,'pending')
                    if value is not None:
                        content = str(value)
                    else:
                        content = str(0)
                    # language = LanguageKey.catch_lang_key_obj(request, 'economy')
                    # context['language'] = language
                    # context['balance_tables'] = balance_tables
                    # # context['order_table_type'] = 'attendee-order'
                    # content = render_to_string('public/tags/balance_table_tag.html', context)

                else:
                    content = ''
            else:
                content = ''



        except Exception as e:
            ErrorR.efail(e)
            content = ''

        pageContents = pageContents.replace('{order_value_pending_order}', content)
        return pageContents

    def replace_multiple_order_value_pending_order(request, pageContents):
        try:
            content = ''
            base_url = request.session['base_url']
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:

                order_table_regex = r"({multiple_order_value_pending_order})"
                oder_table_matches = re.findall(order_table_regex, pageContents)
                if len(oder_table_matches) > 0:
                    context = {}
                    user_id = request.session['event_user']['id']
                    value = EconomyLibrary.get_order_value(user_id,'pending','group-order')
                    if value is not None:
                        content = str(value)
                    else:
                        content = str(0)
                    # language = LanguageKey.catch_lang_key_obj(request, 'economy')
                    # context['language'] = language
                    # context['balance_tables'] = balance_tables
                    # # context['order_table_type'] = 'attendee-order'
                    # content = render_to_string('public/tags/balance_table_tag.html', context)

                else:
                    content = ''
            else:
                content = ''



        except Exception as e:
            ErrorR.efail(e)
            content = ''

        pageContents = pageContents.replace('{multiple_order_value_pending_order}', content)
        return pageContents

    def replace_order_value_open_order(request, pageContents):
        try:
            content = ''
            base_url = request.session['base_url']
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:

                order_table_regex = r"({order_value_open_order})"
                oder_table_matches = re.findall(order_table_regex, pageContents)
                if len(oder_table_matches) > 0:
                    context = {}
                    user_id = request.session['event_user']['id']
                    value = EconomyLibrary.get_order_value(user_id,'open')
                    if value is not None:
                        content = str(value)
                    else:
                        content = str(0)
                    # language = LanguageKey.catch_lang_key_obj(request, 'economy')
                    # context['language'] = language
                    # context['balance_tables'] = balance_tables
                    # # context['order_table_type'] = 'attendee-order'
                    # content = render_to_string('public/tags/balance_table_tag.html', context)

                else:
                    content = ''
            else:
                content = ''



        except Exception as e:
            ErrorR.efail(e)
            content = ''

        pageContents = pageContents.replace('{order_value_open_order}', content)
        return pageContents

    def replace_multiple_order_value_open_order(request, pageContents):
        try:
            content = ''
            base_url = request.session['base_url']
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:

                order_table_regex = r"({multiple_order_value_open_order})"
                oder_table_matches = re.findall(order_table_regex, pageContents)
                if len(oder_table_matches) > 0:
                    context = {}
                    user_id = request.session['event_user']['id']
                    value = EconomyLibrary.get_order_value(user_id,'open','group-order')
                    if value is not None:
                        content = str(value)
                    else:
                        content = str(0)
                    # language = LanguageKey.catch_lang_key_obj(request, 'economy')
                    # context['language'] = language
                    # context['balance_tables'] = balance_tables
                    # # context['order_table_type'] = 'attendee-order'
                    # content = render_to_string('public/tags/balance_table_tag.html', context)

                else:
                    content = ''
            else:
                content = ''



        except Exception as e:
            ErrorR.efail(e)
            content = ''

        pageContents = pageContents.replace('{multiple_order_value_open_order}', content)
        return pageContents

    def replace_order_value_all_order(request, pageContents):
        try:
            content = ''
            base_url = request.session['base_url']
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:

                order_table_regex = r"({order_value_all_order})"
                oder_table_matches = re.findall(order_table_regex, pageContents)
                if len(oder_table_matches) > 0:
                    context = {}
                    user_id = request.session['event_user']['id']
                    value = EconomyLibrary.get_order_value(user_id,'all')
                    if value is not None:
                        content = str(value)
                    else:
                        content = str(0)
                    # language = LanguageKey.catch_lang_key_obj(request, 'economy')
                    # context['language'] = language
                    # context['balance_tables'] = balance_tables
                    # # context['order_table_type'] = 'attendee-order'
                    # content = render_to_string('public/tags/balance_table_tag.html', context)

                else:
                    content = ''
            else:
                content = ''



        except Exception as e:
            ErrorR.efail(e)
            content = ''

        pageContents = pageContents.replace('{order_value_all_order}', content)
        return pageContents

    def replace_multiple_order_value_all_order(request, pageContents):
        try:
            content = ''
            base_url = request.session['base_url']
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:

                order_table_regex = r"({multiple_order_value_all_order})"
                oder_table_matches = re.findall(order_table_regex, pageContents)
                if len(oder_table_matches) > 0:
                    context = {}
                    user_id = request.session['event_user']['id']
                    value = EconomyLibrary.get_order_value(user_id,'all','group-order')
                    if value is not None:
                        content = str(value)
                    else:
                        content = str(0)
                    # language = LanguageKey.catch_lang_key_obj(request, 'economy')
                    # context['language'] = language
                    # context['balance_tables'] = balance_tables
                    # # context['order_table_type'] = 'attendee-order'
                    # content = render_to_string('public/tags/balance_table_tag.html', context)

                else:
                    content = ''
            else:
                content = ''



        except Exception as e:
            ErrorR.efail(e)
            content = ''

        pageContents = pageContents.replace('{multiple_order_value_all_order}', content)
        return pageContents

    def replace_order_value_credit_order(request, pageContents):
        try:
            content = ''
            base_url = request.session['base_url']
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:

                order_table_regex = r"({order_value_credit_order})"
                oder_table_matches = re.findall(order_table_regex, pageContents)
                if len(oder_table_matches) > 0:
                    context = {}
                    user_id = request.session['event_user']['id']
                    value = EconomyLibrary.get_order_value(user_id,'open','attendee-order','credit-order')
                    if value is not None:
                        content = str(value)
                    else:
                        content = str(0)
                    # language = LanguageKey.catch_lang_key_obj(request, 'economy')
                    # context['language'] = language
                    # context['balance_tables'] = balance_tables
                    # # context['order_table_type'] = 'attendee-order'
                    # content = render_to_string('public/tags/balance_table_tag.html', context)

                else:
                    content = ''
            else:
                content = ''



        except Exception as e:
            ErrorR.efail(e)
            content = ''

        pageContents = pageContents.replace('{order_value_credit_order}', content)
        return pageContents

    def replace_multiple_order_value_credit_order(request, pageContents):
        try:
            content = ''
            base_url = request.session['base_url']
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:

                order_table_regex = r"({multiple_order_value_credit_order})"
                oder_table_matches = re.findall(order_table_regex, pageContents)
                if len(oder_table_matches) > 0:
                    context = {}
                    user_id = request.session['event_user']['id']
                    value = EconomyLibrary.get_order_value(user_id,'open','group-order','credit-order')
                    if value is not None:
                        content = str(value)
                    else:
                        content = str(0)
                    # language = LanguageKey.catch_lang_key_obj(request, 'economy')
                    # context['language'] = language
                    # context['balance_tables'] = balance_tables
                    # # context['order_table_type'] = 'attendee-order'
                    # content = render_to_string('public/tags/balance_table_tag.html', context)

                else:
                    content = ''
            else:
                content = ''



        except Exception as e:
            ErrorR.efail(e)
            content = ''

        pageContents = pageContents.replace('{multiple_order_value_credit_order}', content)
        return pageContents

    def replace_reciept(request, pageContents):
        try:
            content = ''
            base_url = request.session['base_url']
            if 'is_user_login' in request.session and request.session['is_user_login'] == True:

                order_table_regex = r"({receipt})"
                oder_table_matches = re.findall(order_table_regex, pageContents)
                if len(oder_table_matches) > 0:
                    context = {}
                    user_id = request.session['event_user']['id']
                    event_id = request.session['event_id']
                    value = EconomyLibrary.get_receipt_data(event_id,user_id)
                    language = LanguageKey.catch_lang_key_obj(request, 'economy')
                    context['language'] = language
                    context['receipts'] = value
                    # # context['order_table_type'] = 'attendee-order'
                    content = render_to_string('public/tags/receipt_tag.html', context)

                else:
                    content = ''
            else:
                content = ''



        except Exception as e:
            ErrorR.efail(e)
            content = ''

        pageContents = pageContents.replace('{receipt}', content)
        return pageContents
