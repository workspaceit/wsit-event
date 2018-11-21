from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
import json
from app.models import StyleSheet, Events
from scss.compiler import compile_string
from django.conf import settings
import boto
from boto.s3.key import Key
import re

from app.views.common_views import EventView
from django.db.models.signals import post_save
from django.dispatch import receiver
from app.views.gbhelper.error_report_helper import ErrorR

class StyleView(generic.DetailView):
    def get(self, request):
        if EventView.check_read_permissions(request, 'css_permission'):
            style = StyleSheet.objects.filter(event_id=request.session['event_auth_user']['event_id'])
            if style.count() > 0:
                css = style[0]
            else:
                css = None

            context = {
                "style": css
            }
            return render(request, 'style/style.html', context)

    def post(self, request):
        response_data = {}
        if EventView.check_permissions(request, 'css_permission'):
            form_data = {
                "style": request.POST.get('style'),
            }
            try:
                style = StyleSheet.objects.filter(event_id=request.session['event_auth_user']['event_id'])
                if style.count() > 0:
                    version = style[0].version+1
                    form_data['version']=version
                    StyleSheet.objects.filter(event_id=request.session['event_auth_user']['event_id']).update(**form_data)
                else:
                    scss = StyleSheet(style=request.POST.get('style'),
                                      event_id=request.session['event_auth_user']['event_id'],
                                      created_by_id=request.session['event_auth_user']['id'])
                    scss.save()

                event_id = request.session['event_auth_user']['event_id']
                event = Events.objects.get(pk=event_id)
                event_url = event.url

                css_data = request.POST.get('style')
                base_url = request.POST.get('base_url')
                css_data = css_data.replace('{base_url}', base_url)
                files_tag = '{0}public/{1}/files/'.format(settings.STATIC_URL_ALT, event_url)
                css_data = css_data.replace('[[files]]', files_tag)
                css_data = css_data.replace('“', '"')
                try:
                    import requests as python_request
                    scss_regex = r"({\import_scss\:)(.|\s|\n)*?(})"
                    match = re.finditer(scss_regex,css_data)
                    for im_css in match:
                        scss_url = im_css.group().split('import_scss:')[1].split('}')[0]
                        scss_url = scss_url.replace('"','').replace("'","")
                        scss_text = python_request.get(scss_url).text
                        ErrorR.okgreen(scss_text)
                        css_data = css_data.replace(im_css.group(),scss_text)
                except Exception as e:
                    ErrorR.elog(e)
                    ErrorR.ilog(e)
                    pass
                compiled_css = compile_string(css_data)
                conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, host=settings.AWS_STORAGE_HOST)
                bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
                extension = 'css'
                key_name = 'public/' + event_url + '/compiled_css/' + 'style' + '.' + extension
                k = Key(bucket)
                k.key = key_name
                if not k.exists():
                    key = bucket.new_key(key_name)
                    key.content_type = 'text/css'
                    key.set_contents_from_string(compiled_css, policy='public-read')
                else:
                    k.content_type = 'text/css'
                    k.set_contents_from_string(compiled_css, policy='public-read')
                response_data['message'] = 'Style Update Successfully'
                response_data['success'] = True
            except Exception as e:
                response_data['message'] = 'Parsing Error'
                response_data['success'] = False
                ErrorR.efail(e)
        else:
            response_data['message'] = 'You do not have Permission to do this'
            response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")

