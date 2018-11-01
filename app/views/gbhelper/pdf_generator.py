import time
import threading
from io import BytesIO
from zipfile import ZipFile
from app.models import Orders, CreditOrders, Attendee, EmailTemplates, Elements, StyleSheet, Setting, Payments, Presets
from django.http import HttpResponse, JsonResponse
from app.views.email_content_view import EmailContentDetailView
from app.views.gbhelper.economy_library import EconomyLibrary
from app.views.gbhelper.language_helper import LanguageH
from django.template.loader import render_to_string
from app.views.gbhelper.error_report_helper import ErrorR
from django.conf import settings
from datetime import datetime
from weasyprint import HTML
from weasyprint.fonts import FontConfiguration
import re


class EconomyPDFGenerator:
    """This class used to generator economy related pdf"""

    def render_pdf(html_content, file_name):
        try:
            font_config = FontConfiguration()
            html = HTML(string=html_content)
            result = html.write_pdf(font_config=font_config)
            # result = html.write_pdf()
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(file_name)
            response['Content-Transfer-Encoding'] = 'binary'
            response.write(result)
            return response
        except Exception as exception:
            print("########### Error to generate pdf ###########")
            ErrorR.efail(exception)
            return HttpResponse('something went wrong')

    def get_receipt(request, event_id, order_number, attendee_id):
        try:
            context = {}
            template = EmailTemplates.objects.filter(name='default-receipt-template', event_id=event_id)
            if template:
                template = template[0]
                order_is_paid = Orders.objects.filter(order_number=order_number, attendee__event_id=event_id,
                                                      status='paid')
                if not order_is_paid:
                    raise ValueError('Order is not paid yet')

                element = Elements.objects.values('id').get(slug='economy')
                attendee = Attendee.objects.get(id=attendee_id)
                context['language'] = LanguageH.get_lang_key(event_id, attendee.language_id, element['id'])
                context['order_table_visible_columns'] = EconomyPDFGenerator.get_order_table_global_settings(event_id)

                html_content = EconomyPDFGenerator.receipt_partial_part(request, context, event_id, template.event.url, template, attendee, order_number)
                response = EconomyPDFGenerator.render_pdf(html_content, 'receipt.pdf')
            else:
                response = EconomyPDFGenerator.render_pdf('Invoice template not found.', 'receipt.pdf')
        except Exception as exception:
            print("########### Error to generate pdf ###########")
            ErrorR.efail(exception)
            response = EconomyPDFGenerator.render_pdf('Something went wrong to generate receipt pdf.', 'receipt.pdf')
        return response

    def receipt_partial_part(request, context, event_id, event_url, template, attendee, order_number):
        context['receipts'] = EconomyLibrary.get_receipt_data(event_id, attendee.id, order_number)
        due_date = context['receipts'][0]['orders'][0]['order']['due_date_datetype']
        invoice_date = context['receipts'][0]['orders'][0]['order']['invoice_date']
        invoice_ref = Payments.objects.get(order_number=order_number).invoice_ref

        body = render_to_string('economy/pdf_elements/receipt.html', context)
        html_content = template.content.replace('{content}', body)
        html_content = EconomyPDFGenerator.replace_economy_templates(request, html_content, order_number, attendee,
                                                                     event_url, due_date,
                                                                     invoice_ref=invoice_ref, invoice_date=invoice_date)
        rec_trance_date = context['receipts'][0]['payment'].created_at
        rec_trance_date = EconomyPDFGenerator.get_formated_date_string(rec_trance_date, attendee.language_id)
        html_content = html_content.replace('{receipt-date}', rec_trance_date)
        html_content = html_content.replace('{transaction-date}', rec_trance_date)
        transaction_id = context['receipts'][0]['payment'].transaction
        html_content = html_content.replace('{transaction-id}', transaction_id if transaction_id else '')
        if type(context['receipts'][0]['payment'].details) is dict:
            card_number = context['receipts'][0]['payment'].details.get('cardNumberMasked')
            card_number = re.sub(r'[a-zA-Z0-9]', r'X', card_number[4:]) + card_number[-4:]
        else:
            card_number = ''
        html_content = html_content.replace('{card-number}', card_number)
        return html_content

    def get_credit_invoice(request, event_id, order_number, attendee_id):
        try:
            context = {}
            template = EmailTemplates.objects.filter(name='default-credit-invoice-template', event_id=event_id)
            if template:
                template = template[0]
                attendee_group_info = EconomyLibrary.get_group_registration_info(attendee_id)
                # need to get group atts, bcoz in group order admin could download credit invoice in other group att's modal
                credit_order = CreditOrders.objects.filter(order__attendee_id__in=attendee_group_info['grp-atts'],
                                                           order_number=order_number, status='open')
                if not credit_order:
                    raise ValueError('Order has no credit.')
                credit_order = credit_order[0]
                attendee = Attendee.objects.get(id=attendee_id)
                element = Elements.objects.values('id').get(slug='economy')
                context['language'] = LanguageH.get_lang_key(event_id, attendee.language_id, element['id'])
                event_url = template.event.url
                html_content = EconomyPDFGenerator.credit_invoice_partial_part(request, context, event_url, template, attendee, credit_order, order_number)
                response = EconomyPDFGenerator.render_pdf(html_content, 'credit_invoice.pdf')
            else:
                response = EconomyPDFGenerator.render_pdf('Invoice template not found.', 'credit_invoice.pdf')
        except Exception as exception:
            print("########### Error to generate pdf ###########")
            ErrorR.efail(exception)
            response = EconomyPDFGenerator.render_pdf('Something went wrong to generate credit-invoice pdf.', 'credit_invoice.pdf')
        return response

    def credit_invoice_partial_part(request, context, event_url, template, attendee, credit_order, order_number):
        context['credit_order'] = {
            'order_number': order_number,
            'cost_excl_vat': credit_order.cost_excluding_vat * -1,
            'cost_incl_vat': credit_order.cost_including_vat * -1,
            'date': credit_order.created_at
        }
        invoice_ref = credit_order.invoice_ref
        body = render_to_string('economy/pdf_elements/credit_invoice.html', context)
        html_content = template.content.replace('{content}', body)
        html_content = EconomyPDFGenerator.replace_economy_templates(request, html_content, order_number, attendee,
                                                                     event_url, invoice_ref=invoice_ref)
        credit_invoice_date = EconomyPDFGenerator.get_formated_date_string(credit_order.created_at, attendee.language_id)
        html_content = html_content.replace('{invoice-date}', credit_invoice_date)
        return html_content

    def get_order_invoice(request, event_id, order_number, attendee_id):
        try:
            context = {}
            template = EmailTemplates.objects.filter(name='default-invoice-template', event_id=event_id)
            if template.exists():
                template = template.first()
                element = Elements.objects.values('id').get(slug='economy')
                attendee = Attendee.objects.get(id=attendee_id)
                context['language'] = LanguageH.get_lang_key(event_id, attendee.language_id, element['id'])
                context['order_table_visible_columns'] = EconomyPDFGenerator.get_order_table_global_settings(event_id)
                html_content = EconomyPDFGenerator.invoice_partial_part(request, event_id, attendee, order_number, context, template, template.event.url)
                response = EconomyPDFGenerator.render_pdf(html_content, 'invoice.pdf')
            else:
                response = EconomyPDFGenerator.render_pdf('Invoice template not found.', 'invoice.pdf')
        except Exception as exception:
            print("########### Error to generate pdf ###########")
            ErrorR.efail(exception)
            response = EconomyPDFGenerator.render_pdf('Something went wrong to generate invoice pdf.', 'invoice.pdf')
        return response

    def invoice_partial_part(request, event_id, attendee, order_number, context, template, event_url):
        order_info = EconomyLibrary.get_order_tables(attendee.id, event_id, True, order_number)
        if order_info['order_type'] == 'group-order':
            context['orders'] = EconomyLibrary.get_group_order_single_table(order_info['order_list'])
        else:
            context['orders'] = order_info['order_list']

        due_date = context['orders'][0]['order']['due_date_datetype']
        invoice_ref = context['orders'][0]['order']['invoice_ref']
        invoice_date = context['orders'][0]['order']['invoice_date']
        context['order_table_type'] = order_info['order_type']
        body = render_to_string('economy/pdf_elements/order_invoice.html', context)
        html_content = template.content.replace('{content}', body)
        html_content = EconomyPDFGenerator.replace_economy_templates(request, html_content, order_number, attendee, event_url,
                                                                     due_date, invoice_ref=invoice_ref, invoice_date=invoice_date)
        return html_content

    def get_order_table_global_settings(event_id):
        default_column_list = ["item_name","cost_excl_vat","rebate_amount","vat_amount","vat_rate","cost_incl_vat"]
        column_settings = Setting.objects.filter(event_id=event_id,name='economy_order_table_global_settings')
        columns = []
        if column_settings.exists():
            if column_settings[0].value != '' and column_settings[0].value !='[]':
                columns = column_settings[0].value
            else:
                columns = default_column_list
        else:
            columns = default_column_list
        return columns

    def replace_economy_templates(request, html_content, order_number, attendee, event_url, due_date=None,invoice_ref=None, invoice_date=None):

            html_content = html_content.replace('{order-number}', order_number)
            html_content = html_content.replace('{invoice-id}', invoice_ref if invoice_ref else '')

            html_content = EmailContentDetailView.replace_questions_variable(request, html_content, attendee, attendee.language_id)
            html_content = EmailContentDetailView.replace_sessions(request, html_content, attendee, attendee.language_id)
            html_content = EmailContentDetailView.replace_travels(request, html_content, attendee, attendee.language_id)
            html_content = EmailContentDetailView.replace_hotels(request, html_content, attendee, attendee.language_id)
            html_content = EmailContentDetailView.replace_general_tags(request, html_content, attendee, attendee.language_id)
            html_content = EmailContentDetailView.replace_economy_tags(request, html_content, attendee, attendee.language_id)
            html_content = EmailContentDetailView.replace_general_questions(request, html_content, attendee, attendee.language_id)
            html_content = EmailContentDetailView.replace_photos(request, html_content, attendee, attendee.language_id)
    #         # get css version
            css_version_obj = StyleSheet.objects.get(event_id=attendee.event_id)
            css_version = css_version_obj.version

            # html_content = html_content.replace('[[file]]', "[[static]]public/[[event_url]]/files")
            # html_content = html_content.replace('[[files]]', "[[static]]public/[[event_url]]/files/")
            # html_content = html_content.replace('[[css]]', "[[static]]public/[[event_url]]/compiled_css/style.css?v="+str(css_version))

            # For Wsit Event
            html_content = html_content.replace('[[file]]', "[[static]]public/files")
            html_content = html_content.replace('[[files]]', "[[static]]public/files/")
            html_content = html_content.replace('[[css]]',
                                                "[[static]]public/compiled_css/main_style.css?v=" + str(
                                                    css_version))

            html_content = html_content.replace('[[static]]', settings.STATIC_URL_ALT)
            html_content = html_content.replace('[[event_url]]', event_url)
            html_content = html_content.replace('[[parmanent]]', settings.STATIC_URL_ALT + 'public/')
            if due_date:
                due_date = EconomyPDFGenerator.get_formated_date_string(due_date, attendee.language_id)
                html_content = html_content.replace('{due-date}', due_date)
                # due_days_cal = due_date - datetime.now()
                # print(type(due_days_cal.days))
                # if due_days_cal.days < 1:
                #     due_days = 0
                # else:
                #     due_days = due_days_cal.days
                due_date_setting = Setting.objects.filter(name='due_date', event_id=attendee.event_id)
                due_days = ''
                if due_date_setting:
                    due_days = due_date_setting[0].value
                html_content = html_content.replace('{due-days}', due_days)
                if invoice_date not in ['None', None]:
                    invoice_date = EconomyPDFGenerator.get_formated_date_string(invoice_date, attendee.language_id)
                else:
                    invoice_date = ''

                html_content = html_content.replace('{invoice-date}', invoice_date)
            return html_content

    def get_formated_date_string(date_value, lang_id):
        try:
            if type(date_value) is str:
                date_value = datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S')
            date_format = Presets.objects.get(id=lang_id).date_format
            compiled_re = re.compile('[a-zA-Z]')
            matched_keys = compiled_re.findall(date_format)
            for key in matched_keys:
                date_format = date_format.replace(key, '%' + key)

            date_string = date_value.strftime(date_format)
        except Exception as excep:
            ErrorR.efail(excep)
            date_string = ''

        return date_string

    def get_html_to_pdf(request, attendee_id, template_id):
        try:
            template = EmailTemplates.objects.get(id=template_id)
            attendee = Attendee.objects.get(id=attendee_id)
            html_content = template.content
            position_head = html_content.index('</head>')
            head_content = "<style> input:before{content: attr(value)} </style>"
            html_content = html_content[:position_head] + head_content + html_content[position_head:]
            html_content = EconomyPDFGenerator.replace_economy_templates(request, html_content, '', attendee, template)
            response = EconomyPDFGenerator.render_pdf(html_content, template.name+'.pdf')
            return response
        except Exception as exception:
            print("########### Error to generate pdf ###########")
            ErrorR.efail(exception)
            response = HttpResponse('Something went wrong.')
        return response


class EconomyPDFExport:
    export_ongoing = False
    export_complete = False
    exported_zipfile = None
    exported_filename = "documents.zip"

    def get_all_event_pdf(request, template_name, task_name):
        result = False
        try:
            event_id = request.session['event_auth_user']['event_id']
            template = EmailTemplates.objects.filter(name=template_name, event_id=event_id)
            if template.exists():
                EconomyPDFExport.export_ongoing = True
                template = template.first()
                task = threading.Thread(target=eval(task_name), args=(request, event_id, template))
                task.start()
                result = True
        except Exception as exception:
            EconomyPDFExport.set_attribute_default(0)
            ErrorR.efail(exception)
        return result

    def pdf_export_invoices_task(request, event_id, template):
        try:
            context = dict()
            sql_query = """SELECT o.id, o.order_number, o.attendee_id FROM orders o INNER JOIN attendees a ON
                        o.attendee_id = a.id WHERE o.status IN ('pending', 'paid') AND a.event_id={} GROUP BY
                        o.order_number ORDER BY o.order_number""".format(event_id)
            all_orders = Orders.objects.raw(sql_query)
            element = Elements.objects.values('id').get(slug='economy')
            language_id = Presets.objects.filter(event_id=event_id).first().id
            context['language'] = LanguageH.get_lang_key(event_id, language_id, element['id'])
            context['order_table_visible_columns'] = EconomyPDFGenerator.get_order_table_global_settings(event_id)
            ct = 0
            byte_file = BytesIO()
            event_url = template.event.url
            font_config = FontConfiguration()
            with ZipFile(byte_file, 'w') as pdf_zip:
                for order in all_orders:
                    attendee_id = order.attendee_id
                    order_number = order.order_number
                    attendee = Attendee.objects.get(id=attendee_id)
                    html_content = EconomyPDFGenerator.invoice_partial_part(request, event_id, attendee, order_number, context, template, event_url)
                    html = HTML(string=html_content)
                    pdf_result = html.write_pdf(font_config=font_config)
                    pdf_zip.writestr("{}.pdf".format(order_number), pdf_result)
                    # ct += 1
                    # if ct == 5:
                    #     print('ct point')
                    #     break
            EconomyPDFExport.exported_zipfile = byte_file
            EconomyPDFExport.export_complete = True
            EconomyPDFExport.exported_filename = "{} - all invoices.zip".format(template.event.name)
        except Exception as ex:
            EconomyPDFExport.set_attribute_default(0)
            ErrorR.efail(ex)

    def pdf_export_receipts_task(request, event_id, template):
        try:
            context = dict()
            sql_query = """SELECT o.id, o.order_number, o.attendee_id FROM orders o INNER JOIN attendees a ON
                        o.attendee_id = a.id WHERE o.status = 'paid' AND a.event_id={} GROUP BY
                        o.order_number ORDER BY o.order_number""".format(event_id)
            all_orders = Orders.objects.raw(sql_query)
            element = Elements.objects.values('id').get(slug='economy')
            language_id = Presets.objects.filter(event_id=event_id).first().id
            context['language'] = LanguageH.get_lang_key(event_id, language_id, element['id'])
            context['order_table_visible_columns'] = EconomyPDFGenerator.get_order_table_global_settings(event_id)
            ct = 0
            byte_file = BytesIO()
            event_url = template.event.url
            font_config = FontConfiguration()
            with ZipFile(byte_file, 'w') as pdf_zip:
                for order in all_orders:
                    attendee_id = order.attendee_id
                    order_number = order.order_number
                    attendee = Attendee.objects.get(id=attendee_id)
                    html_content = EconomyPDFGenerator.receipt_partial_part(request, context, event_id, event_url, template, attendee, order_number)
                    html = HTML(string=html_content)
                    pdf_result = html.write_pdf(font_config=font_config)
                    pdf_zip.writestr("{}.pdf".format(order_number), pdf_result)
                    # ct += 1
                    # if ct == 5:
                    #     print('ct point')
                    #     break
            EconomyPDFExport.exported_zipfile = byte_file
            EconomyPDFExport.export_complete = True
            EconomyPDFExport.exported_filename = "{} - all receipts.zip".format(template.event.name)
        except Exception as ex:
            EconomyPDFExport.set_attribute_default(0)
            ErrorR.efail(ex)

    def pdf_export_credit_invoices_task(request, event_id, template):
        try:
            context = dict()

            credit_orders = CreditOrders.objects.filter(order__attendee__event_id=event_id, status='open').exclude(order__status='cancelled')

            element = Elements.objects.values('id').get(slug='economy')
            language_id = Presets.objects.filter(event_id=event_id).first().id
            context['language'] = LanguageH.get_lang_key(event_id, language_id, element['id'])
            byte_file = BytesIO()
            event_url = template.event.url
            font_config = FontConfiguration()
            with ZipFile(byte_file, 'w') as pdf_zip:
                for credit_order in credit_orders:
                    order_number = credit_order.order_number
                    attendee = credit_order.order.attendee
                    html_content = EconomyPDFGenerator.credit_invoice_partial_part(request, context, event_url, template, attendee, credit_order, order_number)
                    html = HTML(string=html_content)
                    pdf_result = html.write_pdf(font_config=font_config)
                    pdf_zip.writestr("{}.pdf".format(order_number), pdf_result)
            EconomyPDFExport.exported_zipfile = byte_file
            EconomyPDFExport.export_complete = True
            EconomyPDFExport.exported_filename = "{} - all credit orders.zip".format(template.event.name)
        except Exception as ex:
            EconomyPDFExport.set_attribute_default(0)
            ErrorR.efail(ex)

    def check_economy_pdf_export_status(request):
        status_type = request.POST.get('status_type')
        response = dict(message="something went wrong", export=False, complete=False, download_request=True)
        if status_type == "export-request":
            if EconomyPDFExport.export_ongoing:
                response["message"] = "Previous export wasn't complete."
            else:
                pdf_type = request.POST.get('pdf_type')
                result = False
                if pdf_type == "invoice":
                    result = EconomyPDFExport.get_all_event_pdf(request, 'default-invoice-template', 'EconomyPDFExport.pdf_export_invoices_task')
                elif pdf_type == "receipt":
                    result = EconomyPDFExport.get_all_event_pdf(request, 'default-receipt-template', 'EconomyPDFExport.pdf_export_receipts_task')
                elif pdf_type == "credit-invoice":
                    result = EconomyPDFExport.get_all_event_pdf(request, 'default-credit-invoice-template', 'EconomyPDFExport.pdf_export_credit_invoices_task')
                if result:
                    response["message"] = "Export needs couple of minutes."
                    response["export"] = True
                else:
                    response["download_request"] = False
        elif status_type == "export-complete":
            if EconomyPDFExport.export_complete:
                response["message"] = "Export complete."
                response["complete"] = True
        return JsonResponse(response)

    def download_economy_exported_pdf_zip(request):
        if EconomyPDFExport.export_complete and EconomyPDFExport.exported_zipfile:
            zip_filename = EconomyPDFExport.exported_filename
            response = HttpResponse(EconomyPDFExport.exported_zipfile.getvalue(), content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(zip_filename)
            EconomyPDFExport.set_attribute_default(0)
            EconomyPDFExport.exported_filename = "documents.zip"
            return response
        else:
            return HttpResponse("previous export wasn't complete")

    def set_attribute_default(self):
        EconomyPDFExport.export_ongoing = False
        EconomyPDFExport.export_complete = False
        EconomyPDFExport.exported_zipfile = None
