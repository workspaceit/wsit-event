import json, traceback
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.db import transaction
from app.models import EmailTemplates,Events
from django.http import Http404
from django.conf import settings
from boto3.session import Session as boto_session

from app.views.common_views import EventView
from app.views.gbhelper.editor_helper import EditorHelper
from app.views.gbhelper.error_report_helper import ErrorR
from bs4 import BeautifulSoup


class EmailTemplateView(generic.DetailView):
    def get(self, request):
        if EventView.check_read_permissions(request, 'template_permission'):
            # styles = EmailTemplateView.get_style(request.session['event_auth_user']['event_id'])
            email_templates = EmailTemplates.objects.filter(event_id=request.session['event_auth_user']['event_id'], is_show=1, category='email_templates')
            web_pages_templates = EmailTemplates.objects.filter(event_id=request.session['event_auth_user']['event_id'], is_show=1, category='web_pages')
            invoice_templates = EmailTemplates.objects.filter(event_id=request.session['event_auth_user']['event_id'], is_show=1, category='invoices')
            pdf_templates = EmailTemplates.objects.filter(event_id=request.session['event_auth_user']['event_id'], is_show=1, category='pdf')
            context = {
                'email_templates': email_templates,
                'web_pages_templates': web_pages_templates,
                'invoice_templates': invoice_templates,
                'pdf_templates': pdf_templates
            }
            return render(request, 'email_template/templates.html', context)

    @transaction.atomic
    def post(self, request):
        if EventView.check_permissions(request, 'template_permission'):
            try:
                response_data = {}
                event_id = request.session['event_auth_user']['event_id']
                admin_id = request.session['event_auth_user']['id']
                template_category = request.POST.get('template_category')
                if 'id' in request.POST:
                    template_id = request.POST.get('id')
                    if 'content' in request.POST:
                        data = json.loads(request.POST.get('content'))
                        # content = data['content'].replace(settings.STATIC_URL_ALT, '[[static]]')
                        EmailTemplates.objects.filter(id=template_id).update(content=data, last_updated_by_id=admin_id)
                        response_data = {
                            'success': True,
                            'message': 'Template Updated'
                        }
                    else:
                        template_name = request.POST.get('template_name')
                        old_template = EmailTemplates.objects.get(id = template_id)
                        default_templates = ["default-web-template","default-email-template","default-invoice-template","default-credit-invoice-template","default-receipt-template"]
                        if old_template.name in default_templates:
                            template_name = old_template.name
                        # if old_template.name == 'default-web-template':
                        #     template_name = 'default-web-template'
                        # elif old_template.name == 'default-email-template':
                        #     template_name = 'default-email-template'
                        name = EmailTemplates.objects.filter(name=template_name, event_id=event_id, is_show=1).exclude(id=template_id)
                        if not name.exists():
                            EmailTemplates.objects.filter(id=template_id).update(name=template_name, category=template_category, last_updated_by_id=admin_id)
                            template = EmailTemplates.objects.get(id=template_id)
                            response_data = {
                                'success': True,
                                'message': 'Template Updated',
                                'template': template.as_dict()
                            }
                        else:
                            response_data = {
                                'error': True,
                                'message': 'Template Name already Exist'
                            }
                else:
                    template_name = request.POST.get('template_name')
                    name = EmailTemplates.objects.filter(name=template_name, event_id=event_id, is_show=1)
                    style_files = ""
                    script_files = ""
                    if template_category == "web_pages" or template_category == "pdf":
                        style_files = """<link rel="stylesheet" type="text/css" href="[[css]]" />"""
                        # styles = EmailTemplateView.get_style(event_id)
                        # for style in styles['css']:
                        #     style_files+= """<link rel="stylesheet" type="text/css" href='"""+style+"""' />"""
                        # script_files = """<script type="text/javascript" src='public/js/jquery.min.js'></script>"""
                    if not name.exists():
                        content = """<!DOCTYPE html>
                        <html lang=sv-se>
                            <head>
                                <meta charset=utf-8>
                                <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                """+style_files+"""
                                <style>
                                </style>
                            </head>
                            <body>
                                <div class="section header">
                                </div>
                                {content}
                                <div class="section footer">
                                </div>
                            </body>
                        </html>"""
                        template_content = EmailTemplates(name=template_name, category=template_category, content=content, created_by_id=admin_id,
                                                   last_updated_by_id=admin_id,
                                                   event_id=event_id)
                        template_content.save()
                        response_data = {
                            'success': True,
                            'message': 'Template created',
                            'template': template_content.as_dict()
                        }
                    else:
                        response_data = {
                            'error': True,
                            'message': 'Template Name already Exist'
                        }
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            except Exception as e:
                print(e)
                print(traceback.print_exc())
                response_data = {
                    'error': True,
                    'message': 'Something went wrong. Please try again.'
                }
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            response_data = {
                'error': True,
                'message': 'You do not have Permission to do this'
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")


    def delete(request):
        response_data = {}
        if EventView.check_permissions(request, 'template_permission'):
            template_id = request.POST.get('id')
            template = EmailTemplates.objects.get(id=template_id)
            default_templates = ["default-web-template","default-email-template","default-invoice-template","default-credit-invoice-template","default-receipt-template"]
            # if template.name == 'default-web-template' or template.name == 'default-email-template':
            if template.name in default_templates:
                response_data['warning'] = "You can't delete the Default template"
            else:
                EmailTemplates.objects.filter(id=template_id).update(is_show=0)
                response_data['success'] = "Template Deleted Successfully"
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_style(event_id):
        event = Events.objects.get(pk=event_id)
        event_url = event.url
        session = boto_session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                  region_name='eu-west-1')
        s3_client = session.client('s3')
        s3_response = s3_client.list_objects(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Prefix='public/' + event_url +'/compiled_css/style'
        )
        css_files = []
        if 'Contents' in s3_response:
            files = s3_response['Contents']
            page_images = []
            for file in files:
                key = file['Key']
                url = '{}/{}/{}'.format(s3_client.meta.endpoint_url, settings.AWS_STORAGE_BUCKET_NAME, key)
                url = url.replace(settings.STATIC_URL_ALT, '[[static]]')
                url = '[[static]]public/[[event_url]]/compiled_css/style.css'
                css_files.append(url)
                print(url)
        return {'css':css_files}



class EmailTemplateDetailView(generic.DetailView):

    def get_object(self, pk):
        try:
            template = EmailTemplates.objects.filter(id=pk,event_id=self.request.session['event_auth_user']['event_id'])
            if template.exists():
                return template[0]
            else:
                raise Http404
        except EmailTemplates.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        if EventView.check_permissions(request, 'template_permission'):
            template_content = self.get_object(pk)
            styles = False
            iframe_style = ''
            if template_content.category == 'web_pages':
                template_content.content = template_content.content.replace('{content}','<p>{content}</p>')
                styles = True
                # iframe_style = '#content-body-data{margin-top: 60px;}'
            content = BeautifulSoup(template_content.content,'html5lib')
            editor_common_context = EditorHelper.get_editor_context(request,styles=styles,fullpage=True,iframe_style=iframe_style)
            context={
                "template_content":template_content,
                "content": content.prettify()
            }
            context.update(editor_common_context)
            return render(request, 'email_template/template_editor.html',context)
            # return render(request, 'email_template/edit_template.html',context)
        else:
            raise Http404

    def get_template(request, pk):
        template = EmailTemplates.objects.get(pk=pk)
        response = {
            'success': True,
            'template': template.as_dict()
        }
        return HttpResponse(json.dumps(response), content_type='application/json')