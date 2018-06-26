from django.views import generic
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from app.models import Rebates ,Session ,Travel , Room,Orders,CreditOrders,Payments,PresetEvent
import json
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from app.views.common_views import EventView
from django.db.models import Q,Max, Sum, F
from io import StringIO, BytesIO
from app.views.gbhelper.error_report_helper import ErrorR
from app.views.gbhelper.pdf_generator import EconomyPDFGenerator, EconomyPDFExport

from app.views.gbhelper.language_helper import LanguageH


class EconomyView(generic.DetailView):

    def isint(x):
        try:
            a = float(x)
            b = int(a)
        except ValueError:
            return False
        else:
            return a == b

    def get_economy_overview(request):
        context={}
        event_id = request.session['event_auth_user']['event_id']
        language = PresetEvent.objects.filter(event_id=event_id)
        if language:
            language_id = language[0].preset_id
        response = LanguageH.catch_lang_key_multiple(language_id, 'economy', ['economy_txt_currency'])
        currency_text = response['langkey']['economy_txt_currency']
        context['overview_data'] = EconomyView.get_overview_data(request)
        context['overview_table'] = EconomyView.get_overview_order_table_data(request)
        context['currency_text'] = currency_text
        return render(request, 'economy/overview.html', context)

    def get_economy_overview_report(request):
        overview_data =EconomyView.get_overview_data(request)
        overview_table =EconomyView.get_overview_order_table_data(request)

        event_id = request.session['event_auth_user']['event_id']
        language = PresetEvent.objects.filter(event_id=event_id)
        if language:
            language_id = language[0].preset_id
        response = LanguageH.catch_lang_key_multiple(language_id, 'economy', ['economy_txt_currency'])
        currency_text = response['langkey']['economy_txt_currency']

        data_list =[['Value','Sum incl. VAT','Sum excl. VAT','%']]
        for data in overview_table:
            list = []
            list.append(str(data['name']))
            list.append(str(data['value']))
            list.append('')
            list.append('')
            data_list.append(list)

        for data in overview_data:
            list=[]
            list.append(str(data['name']))
            if data['name'] != 'Orders':
                list.append(str(data['sum_incl_vat'])+' '+str(currency_text))
                list.append(str(data['sum_excl_vat'])+' '+str(currency_text))
            else:
                list.append(str(data['sum_incl_vat']))
                list.append(str(data['sum_excl_vat']))

            if data['percentage']!='':
                percentage = float(data['percentage'])
                if not EconomyView.isint(percentage):
                    percentage = '{:0,.2f}'.format(percentage).replace(",", " ")
                else:
                    percentage = '{0:,}'.format(int(percentage)).replace(",", " ")
                list.append(str(percentage)+str('%'))
            else:
                list.append(str(data['percentage']))
            data_list.append(list)

        # headers = ['Value','Sum incl. Vat','Sum excl. Vat','%']
        wb = Workbook()
        ws = wb.active
        all_rows = data_list
        
        for row in all_rows:
            ws.append(row)

        f = BytesIO()
        wb.save(f)
        response = HttpResponse(save_virtual_workbook(wb), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="economy-report.xlsx"'
        return response

    def get_overview_order_table_data(request):
        overview_data = []
        event_id = request.session['event_auth_user']['event_id']
        # --------------------------total orders
        total_orders = Orders.objects.filter(~Q(status='cancelled'), attendee__event_id=event_id).values(
            'order_number').distinct().count()
        obj = {
            'name': 'Orders',
            'value': total_orders
        }
        overview_data.append(obj)

        # ----------------------------- annuled order
        annuled_orders = Orders.objects.filter(attendee__event_id=event_id,
                                                             status__in=['cancelled']).values('order_number').distinct().count()
        obj = {
            'name': 'Annulled orders',
            'value': annuled_orders,
        }
        overview_data.append(obj)

        # ----------------------------- settled order
        # settled_orders = Orders.objects.filter(attendee__event_id=event_id,
        #                                        status__in=['paid']).values('order_number').distinct().count()
        # obj = {
        #     'name': 'Settled orders',
        #     'value': settled_orders,
        # }
        # overview_data.append(obj)

        # ----------------------------- open order
        open_orders = Orders.objects.filter(attendee__event_id=event_id,
                                               status__in=['open']).values('order_number').distinct().count()
        obj = {
            'name': 'Open orders',
            'value': open_orders
        }
        overview_data.append(obj)

        # -------------------------------------------------------credited
        credit_orders = CreditOrders.objects.filter(order__attendee__event_id=event_id,status__in=['open']).values('order_number').distinct().count()

        obj = {
            'name': 'Credited orders',
            'value': credit_orders,
        }
        overview_data.append(obj)

        #--------------------------Over due order
        over_due_order_count = 0
        unsettled_orders = Orders.objects.filter(attendee__event_id=event_id, status__in=['pending'])
        for order in unsettled_orders:
            if order.get_past_due():
                over_due_order_count += 1
        obj = {
            'name': 'Orders Over Due',
            'value': over_due_order_count,
        }
        overview_data.append(obj)
        return overview_data

    def get_overview_data(request):
        overview_data = []
        event_id = request.session['event_auth_user']['event_id']
        # --------------------------total orders
        # total_orders = Orders.objects.filter(~Q(status='cancelled'), attendee__event_id=event_id).values(
        #     'order_number').distinct().count()
        # obj = {
        #     'name': 'Orders',
        #     'sum_incl_vat': total_orders,
        #     'sum_excl_vat': total_orders,
        #     'percentage': ''
        # }
        # overview_data.append(obj)

        # ---------------------------calculated turnover
        calculated_turned_over_excl_vat = Orders.objects.filter(attendee__event_id=event_id,
                                                                status__in=['paid', 'pending']).aggregate(
            total=Sum(F('cost')))
        calculated_turned_over_incl_vat = Orders.objects.filter(attendee__event_id=event_id,
                                                                status__in=['paid', 'pending']).aggregate(
            total=Sum(F('cost') + F('vat_amount')))
        calculated_turned_over_excl_vat_amount = 0
        if calculated_turned_over_excl_vat['total'] is not None:
            calculated_turned_over_excl_vat_amount = calculated_turned_over_excl_vat['total']

        calculated_turned_over_incl_vat_amount = 0
        if calculated_turned_over_incl_vat['total'] is not None:
            calculated_turned_over_incl_vat_amount = calculated_turned_over_incl_vat['total']

        obj = {
            'name': 'Calculated Turnover',
            'sum_incl_vat': calculated_turned_over_incl_vat_amount,
            'sum_excl_vat': calculated_turned_over_excl_vat_amount,
            'percentage': ''
        }
        overview_data.append(obj)

        # ----------------------------settled order
        settled_orders = Orders.objects.filter(attendee__event_id=event_id, status__in=['paid'])
        settled_order_value_excl_vat = settled_orders.aggregate(total=Sum(F('cost')))
        settled_order_value_incl_vat = settled_orders.aggregate(total=Sum(F('cost') + F('vat_amount')))

        settled_order_value_excl_vat_amount = 0
        if settled_order_value_excl_vat['total'] is not None:
            settled_order_value_excl_vat_amount = settled_order_value_excl_vat['total']

        settled_order_value_incl_vat_amount = 0
        if settled_order_value_incl_vat['total'] is not None:
            settled_order_value_incl_vat_amount = settled_order_value_incl_vat['total']

        settled_order_value_percentage = 0
        if calculated_turned_over_excl_vat_amount != 0:
            settled_order_value_percentage = (
                                             settled_order_value_excl_vat_amount / calculated_turned_over_excl_vat_amount) * 100

        obj = {
            'name': 'Settled',
            'sum_incl_vat': settled_order_value_incl_vat_amount,
            'sum_excl_vat': settled_order_value_excl_vat_amount,
            'percentage': settled_order_value_percentage
        }
        overview_data.append(obj)

        # -------------------------------settled by card
        settled_orders_order_number = settled_orders.values('order_number').distinct()
        payments_by_card_order_numbers = Payments.objects.filter(method='dibs',
                                                                 order_number__in=settled_orders_order_number).values(
            'order_number')
        payment_by_card_orders = settled_orders.filter(order_number__in=payments_by_card_order_numbers)

        settled_by_card_excl_vat_amount = 0
        settled_by_card_incl_vat_amount = 0
        for order in payment_by_card_orders:
            settled_by_card_excl_vat_amount += order.cost
            settled_by_card_incl_vat_amount += order.get_total_cost()

        settled_by_card_value_percentage = 0
        if calculated_turned_over_excl_vat_amount != 0:
            settled_by_card_value_percentage = (
                                               settled_by_card_excl_vat_amount / calculated_turned_over_excl_vat_amount) * 100
        obj = {
            'name': 'Settled By Card',
            'sum_incl_vat': settled_by_card_incl_vat_amount,
            'sum_excl_vat': settled_by_card_excl_vat_amount,
            'percentage': settled_by_card_value_percentage
        }
        overview_data.append(obj)

        # -------------------------------settled by invoice
        settled_orders_order_number = settled_orders.values('order_number').distinct()
        payments_by_invoice_order_numbers = Payments.objects.filter(method='admin',
                                                                    order_number__in=settled_orders_order_number).values(
            'order_number')
        payment_by_invoice_orders = settled_orders.filter(order_number__in=payments_by_invoice_order_numbers)

        settled_by_invoice_excl_vat_amount = 0
        settled_by_invoice_incl_vat_amount = 0
        for order in payment_by_invoice_orders:
            settled_by_invoice_excl_vat_amount += order.cost
            settled_by_invoice_incl_vat_amount += order.get_total_cost()

        settled_by_invoice_value_percentage = 0
        if calculated_turned_over_excl_vat_amount != 0:
            settled_by_invoice_value_percentage = (
                                                  settled_by_invoice_excl_vat_amount / calculated_turned_over_excl_vat_amount) * 100

        obj = {
            'name': 'Settled By Invoice',
            'sum_incl_vat': settled_by_invoice_incl_vat_amount,
            'sum_excl_vat': settled_by_invoice_excl_vat_amount,
            'percentage': settled_by_invoice_value_percentage
        }
        overview_data.append(obj)

        # -----------------------------------unsettled order
        unsettled_orders = Orders.objects.filter(attendee__event_id=event_id, status__in=['pending'])
        unsettled_order_value_excl_vat = unsettled_orders.aggregate(total=Sum(F('cost')))
        unsettled_order_value_incl_vat = unsettled_orders.aggregate(total=Sum(F('cost') + F('vat_amount')))

        unsettled_order_value_excl_vat_amount = 0
        if unsettled_order_value_excl_vat['total'] is not None:
            unsettled_order_value_excl_vat_amount = unsettled_order_value_excl_vat['total']

        unsettled_order_value_incl_vat_amount = 0
        if unsettled_order_value_incl_vat['total'] is not None:
            unsettled_order_value_incl_vat_amount = unsettled_order_value_incl_vat['total']

        unsettled_order_value_percentage = 0
        if calculated_turned_over_excl_vat_amount != 0:
            unsettled_order_value_percentage = (
                                               unsettled_order_value_excl_vat_amount / calculated_turned_over_excl_vat_amount) * 100

        obj = {
            'name': 'Unsettled',
            'sum_incl_vat': unsettled_order_value_incl_vat_amount,
            'sum_excl_vat': unsettled_order_value_excl_vat_amount,
            'percentage': unsettled_order_value_percentage
        }
        overview_data.append(obj)

        # ------------------------------------------------overdue

        over_due_order_value_excl_vat_amout = 0
        over_due_order_value_incl_vat_amout = 0

        for order in unsettled_orders:
            if order.get_past_due():
                over_due_order_value_excl_vat_amout += order.cost
                over_due_order_value_incl_vat_amout += order.get_total_cost()

        overdue_order_value_percentage = 0
        if unsettled_order_value_excl_vat_amount != 0:
            overdue_order_value_percentage = (
                                             over_due_order_value_excl_vat_amout / unsettled_order_value_excl_vat_amount) * 100

        obj = {
            'name': 'Over Due',
            'sum_incl_vat': over_due_order_value_incl_vat_amout,
            'sum_excl_vat': over_due_order_value_excl_vat_amout,
            'percentage': overdue_order_value_percentage
        }
        overview_data.append(obj)

        # ----------------------------- annuled order
        annuled_order_value_excl_vat = Orders.objects.filter(attendee__event_id=event_id,
                                                             status__in=['cancelled']).aggregate(total=Sum(F('cost')))
        annuled_order_value_incl_vat = Orders.objects.filter(attendee__event_id=event_id,
                                                             status__in=['cancelled']).aggregate(
            total=Sum(F('cost') + F('vat_amount')))

        annuled_order_value_excl_vat_amount = 0
        if annuled_order_value_excl_vat['total'] is not None:
            annuled_order_value_excl_vat_amount = annuled_order_value_excl_vat['total']

        annuled_order_value_incl_vat_amount = 0
        if annuled_order_value_incl_vat['total'] is not None:
            annuled_order_value_incl_vat_amount = annuled_order_value_incl_vat['total']

        obj = {
            'name': 'Annulled Order Value',
            'sum_incl_vat': annuled_order_value_incl_vat_amount,
            'sum_excl_vat': annuled_order_value_excl_vat_amount,
            'percentage': ''
        }
        overview_data.append(obj)

        # ----------------------------------------------- open order
        open_order_value_excl_vat = Orders.objects.filter(attendee__event_id=event_id, attendee__status='registered',
                                                          status__in=['open']).aggregate(
            total=Sum(F('cost')))
        open_order_value_incl_vat = Orders.objects.filter(attendee__event_id=event_id, attendee__status='registered',
                                                          status__in=['open']).aggregate(
            total=Sum(F('cost') + F('vat_amount')))

        open_order_value_excl_vat_amount = 0
        if open_order_value_excl_vat['total'] is not None:
            open_order_value_excl_vat_amount = open_order_value_excl_vat['total']

        open_order_value_incl_vat_amount = 0
        if open_order_value_incl_vat['total'] is not None:
            open_order_value_incl_vat_amount = open_order_value_incl_vat['total']

        obj = {
            'name': 'Open Order Value',
            'sum_incl_vat': open_order_value_incl_vat_amount,
            'sum_excl_vat': open_order_value_excl_vat_amount,
            'percentage': ''
        }
        overview_data.append(obj)

        # -------------------------------------------------------credited
        credit_order_value_excl_vat = CreditOrders.objects.filter(order__attendee__event_id=event_id,
                                                                  status__in=['open']).aggregate(
            total=Sum(F('cost_excluding_vat')))
        credit_order_value_incl_vat = CreditOrders.objects.filter(order__attendee__event_id=event_id,
                                                                  status__in=['open']).aggregate(
            total=Sum(F('cost_including_vat')))

        credit_order_value_excl_vat_amount = 0
        credit_order_value_incl_vat_amount = 0

        if credit_order_value_excl_vat['total'] is not None:
            credit_order_value_excl_vat_amount = credit_order_value_excl_vat['total']

        if credit_order_value_incl_vat['total'] is not None:
            credit_order_value_incl_vat_amount = credit_order_value_incl_vat['total']

        obj = {
            'name': 'Credited Order Value',
            'sum_incl_vat': credit_order_value_incl_vat_amount,
            'sum_excl_vat': credit_order_value_excl_vat_amount,
            'percentage': ''
        }
        overview_data.append(obj)
        return overview_data

    def get_rebate_view(request):
        if EventView.check_read_permissions(request, 'economy_permission'):
            context = {}
            event_id = request.session['event_auth_user']['event_id']
            rebates = Rebates.objects.filter(event_id=event_id)
            sessions = Session.objects.filter(group__event_id=event_id)
            travels = Travel.objects.filter(group__event_id=event_id)
            rooms = Room.objects.filter(hotel__group__event_id=event_id)
            context['rebates'] = rebates
            context['sessions']=sessions
            context['travels']=travels
            context['rooms']=rooms
            return render(request, 'economy/rebate.html', context)

    def add_edit_rebate(request):
        response_data = {'success': True}
        if EventView.check_permissions(request, 'economy_permission'):
            event_id = request.session['event_auth_user']['event_id']
            name = request.POST.get('name')
            item_id= request.POST.get('item_id')
            items = json.loads(item_id)
            sessions =[]
            travels=[]
            rooms=[]
            for item in items:
                if item.startswith("session"):
                   sessions.append(item.split("-")[1])
                if item.startswith("room"):
                   rooms.append(item.split("-")[1])
                if item.startswith("travel"):
                   travels.append(item.split("-")[1])

            items_ids = {
                "sessions":sessions,
                "rooms":rooms,
                "travels":travels
            }

            items_ids=json.dumps(items_ids)
            rebate_type = request.POST.get('rebate_type')
            value = request.POST.get('value')
            rebate_id = request.POST.get('rebate_id')
            print('rebate_id type: {}'.format(type(rebate_id)))

            try:
                if rebate_id and rebate_id.isdigit():
                    rebate = Rebates.objects.get(id=rebate_id)
                    rebate.name = name
                    rebate.type_id = items_ids
                    rebate.rebate_type = rebate_type
                    rebate.value = value
                    rebate.save()
                    response_data['rebate'] = rebate.as_dict()
                    response_data['msg'] = 'Rebate is updated successfully.'
                else:
                    admin_id = request.session['event_auth_user']['id']
                    rebate = Rebates(name=name, type_id=items_ids, rebate_type=rebate_type, value=value, event_id=event_id, created_by_id=admin_id)
                    rebate.save()
                    response_data['rebate'] = rebate.as_dict()
                    response_data['msg'] = 'Rebate is created successfully.'

            except Exception as exception:
                print(exception)
                response_data['success'] = False
                response_data['msg'] = 'Error occurred in rebate operation.'
        else:
            response_data['success'] = False
            response_data['msg'] = 'You do not have Permission to do this'
        return JsonResponse(response_data, safe=True)

    def delete_rebate(request):
        response_data = {'success': True}
        if EventView.check_permissions(request, 'economy_permission'):
            rebate_id = request.POST.get('rebate_id')
            try:
                Rebates.objects.get(id=rebate_id).delete()
                response_data['msg'] = 'Rebate is deleted successfully.'
            except Exception as exception:
                print(exception)
                response_data['success'] = False
                response_data['msg'] = 'Error occurred to delete rebate.'
        else:
            response_data['success'] = False
            response_data['msg'] = 'You do not have Permission to do this'
        return JsonResponse(response_data, safe=True)

    def get_all_rebates(request):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        all_rebates = Rebates.objects.filter(event_id=event_id)
        rebates = []
        for rebate in all_rebates:
            rebates.append(rebate.as_dict())

        response_data['rebates'] = rebates
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def export_all_pdf_view(request):
        context = dict()
        context['item_list'] = [
            dict(name="Invoices", type="invoice"),
            dict(name="Receipts", type="receipt"),
            dict(name="Credit invoices", type="credit-invoice")
        ]
        return render(request, 'economy/export.html', context)

    # def economy_export_download(request):
    #     response = HttpResponse('Something went wrong.')
    #     try:
    #         event_id = request.session['event_auth_user']['event_id']
    #         pdf_type = request.GET.get('pdf_type')
    #         if pdf_type == 'invoice':
    #             response = EconomyPDFExport.get_all_event_invoices(request, event_id)
    #         elif pdf_type == 'receipt':
    #             response = EconomyPDFGenerator.get_all_event_invoices(request, event_id)
    #         elif pdf_type == 'credit-invoice':
    #             response = EconomyPDFGenerator.get_all_event_invoices(request, event_id)
    #     except Exception as ex:
    #         ErrorR.efail(ex)
    #     return response

    def economy_export_check_status(request):
        return EconomyPDFExport.check_economy_pdf_export_status(request)

    def economy_export_download_zipfile(request):
        return EconomyPDFExport.download_economy_exported_pdf_zip(request)
