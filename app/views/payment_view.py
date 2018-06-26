from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
import json
from app.models import StyleSheet, Events ,PaymentSettings
from django.conf import settings


from app.views.common_views import EventView


class PaymentView(generic.DetailView):
    def get(self, request):
        if EventView.check_read_permissions(request, 'economy_permission'):
            payment_setting = PaymentSettings.objects.filter(event_id=request.session['event_auth_user']['event_id'])
            if payment_setting.count() > 0:
                payment = payment_setting[0]
            else:
                payment = None

            context = {
                "payment": payment
            }
            return render(request, 'payment/payment.html', context)

    def post(self, request):
        response_data = {}
        currency= request.POST.get('currency')
        merchant_id = request.POST.get('merchant_id')
        payment_types = request.POST.get('payment_types')
        key1 = request.POST.get('key1')
        key2 = request.POST.get('key2')
        form_data = {
            "currency": currency,
            "merchant_id": merchant_id,
            "payment_types": payment_types,
            "key1": key1,
            "key2":key2,
        }
        try:
            payment = PaymentSettings.objects.filter(event_id=request.session['event_auth_user']['event_id'])
            if payment.count() > 0:
                PaymentSettings.objects.filter(event_id=request.session['event_auth_user']['event_id']).update(**form_data)
            else:
                payment = PaymentSettings(currency=currency,merchant_id=merchant_id,payment_types=payment_types,key1=key1,key2=key2,
                                  event_id=request.session['event_auth_user']['event_id'],
                                  created_by_id=request.session['event_auth_user']['id'])
                payment.save()
            response_data['message'] = "Payment setting update successfully"
            response_data['success'] = True
        except Exception as e:
            response_data['message'] = 'Parsing Error'
            response_data['success'] = False
            print(str(e))

        return HttpResponse(json.dumps(response_data), content_type="application/json")
