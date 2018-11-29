from django.http import JsonResponse
from django.views import generic
from app.models import  PaymentSettings
from django.conf import settings
from app.views.gbhelper.economy_library import EconomyLibrary
from django.views.decorators.csrf import csrf_exempt
import json, hashlib, math
from publicfront.views.page2 import DynamicPage


class Payment(generic.TemplateView):

    def get_order_info_for_payment(request, *args, **kwargs):
        context = {'result': False}
        if 'is_user_login' in request.session and request.session['is_user_login']:
            event_id = request.session['event_id']
            payment_setting = PaymentSettings.objects.get(event_id=event_id)
            if payment_setting:
                order_number = request.POST.get('order_number')
                amount = EconomyLibrary.get_total_payable_amount_for_order(order_number)
                context['amount'] = math.ceil(amount * 100)
                context['action_url'] = settings.DIBS_ACTION_URL
                context['accept_url'] = settings.DIBS_ACCEPT_URL
                context['accept_return_url'] = settings.DIBS_ACCEPT_RETURN_URL
                context['cancelurl'] = settings.DIBS_CANCEL_URL
                # context['test'] = settings.DIBS_TEST


                context['currency'] = payment_setting.currency
                context['merchant'] = payment_setting.merchant_id
                context['payment_types'] = payment_setting.payment_types

                # project id in dibs is decided by account
                context['account']=event_id

                key1 = payment_setting.key1
                key2= payment_setting.key2
                key_str1=key1+"merchant="+payment_setting.merchant_id+"&orderid="+order_number+"&‌currency="+payment_setting.currency+"&amount="+str(context['amount'])
                md1 = hashlib.md5(key_str1.encode('utf-8')).hexdigest()
                md5key_str = key2+md1
                context['md5key']=hashlib.md5(md5key_str.encode('utf-8')).hexdigest()
                context['result'] = True
            else:
                context['result'] = False

        return JsonResponse(context)

    @csrf_exempt
    def payment_callback_success(request,*args, **kwargs):
        details=json.dumps(request.POST)
        order_number = request.POST.get('orderid')
        amount = request.POST.get('amount')
        amount = float(amount)/100
        transaction= request.POST.get('transaction')
        status = request.POST.get('status')
        if status =='ACCEPTED':
            EconomyLibrary.make_order_paid(order_number, amount, transaction, 'dibs', details, 'pending')
            return DynamicPage.get_static_page(request, 'payment-success', True, *args, **kwargs)

    @csrf_exempt
    def payment_callback_cancel(request, *args, **kwargs):
        return DynamicPage.get_static_page(request, 'payment-cancel', True, *args, **kwargs)
