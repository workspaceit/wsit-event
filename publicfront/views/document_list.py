import boto
from boto3.session import Session as boto_session

from django.shortcuts import render, redirect
from django.views import generic
from app.models import Attendee, Answers, EmailTemplates, Elements, EmailContents, StyleSheet
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.staticfiles.templatetags.staticfiles import static
import re
from publicfront.views.page2 import DynamicPage


class DocumentDetail(generic.DetailView):
    def get(self, request, *args, **kwargs):
        try:
            event_id = request.session["event_id"]
            template = EmailTemplates.objects.filter(name="default-web-template", event_id=event_id)
            if template.exists():
                # get css version
                css_version_obj = StyleSheet.objects.get(event_id=request.session['event_id'])
                css_version = css_version_obj.version
                template_content = template[0].content.replace('[[file]]', "[[static]]public/[[event_url]]/files")
                template_content = template[0].content.replace('[[files]]', "[[static]]public/[[event_url]]/files/")
                template_content = template_content.replace('[[css]]',
                                                            "[[static]]public/[[event_url]]/compiled_css/style.css?v="+str(css_version))
                template_content = template_content.replace('[[static]]', settings.STATIC_URL_ALT)
                template_content = template_content.replace('public/js/jquery.min.js',
                                                            static('public/js/jquery.min.js'))
                template_content = template_content.replace('[[event_url]]', template[0].event.url)
                template_content = template_content.replace('[[parmanent]]', settings.STATIC_URL_ALT + 'public/')
                element = Elements.objects.filter(slug="login-form")
                context = DocumentDetail.document_list(request)
                content = render_to_string('public/document_list/index.html', context)
                page_content = template_content.replace('{content}', content)
                menu_find = re.findall(r'{(menu)}', page_content)
                if len(menu_find) > 0:
                    menu = DynamicPage.get_menu(request)
                    page_content = page_content.replace('{menu}', menu)
                context = {
                    'page_content': page_content
                }
                # return render(request, 'public/attendee/login_page.html', context)
                return render(request, 'public/static_pages/cms_page.html', context)
            else:
                return redirect('welcome', event_url=request.session['event_url'])
        except Exception as e:
            import os, sys
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return redirect('welcome', event_url=request.session['event_url'])

    def document_list(request):
        try:
            conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
            event_url = request.session['event_url']
            session = boto_session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                   aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                   region_name='eu-west-1')
            s3_client = session.client('s3')
            fileList = []
            # url = "public/"+event_url
            url = "public/" + event_url + "/files"
            files = bucket.list(prefix=url)
            for file in files:
                fileList.append(file.name)
            objList = []
            rootdict = {
                'text': 'files',
                'parent_id': 'root',
                'expanded': True,
                'spriteCssClass': 'rootfolder',
                'path': url + "/"
            }
            objList.append(rootdict)
            for obj in fileList:
                str = obj.split("/")
                depth_level = len(str)
                path = url
                for index in range(2, depth_level):
                    if index + 1 < depth_level:
                        if str[index + 1] != '':
                            dict = {}
                            dict['text'] = str[index + 1]
                            path = path + "/" + str[index + 1]
                            dict['parent_id'] = str[index]
                            dict['path'] = path

                            dict['expanded'] = True
                            file = str[index + 1].rsplit(".", 1)
                            if len(file) == 1:
                                dict['spriteCssClass'] = 'folder'
                            else:
                                if file[1].lower() == "png" or file[1].lower() == "jpeg" or file[1].lower() == "jpg":
                                    dict['spriteCssClass'] = 'image'
                                elif file[1].lower() == "css" or file[1].lower() == "html":
                                    dict['spriteCssClass'] = 'file'
                                elif file[1].lower() == "pdf":
                                    dict['spriteCssClass'] = 'file'
                                elif file[1].lower() == "txt":
                                    dict['spriteCssClass'] = 'file'
                                else:
                                    dict['spriteCssClass'] = 'file'

                            found = False
                            for object in objList:
                                if object['text'] == dict['text'] and object['parent_id'] == dict['parent_id']:
                                    found = True
                                    break
                            if not found:
                                objList.append(dict)

            ph = DocumentDetail.buildTree(objList)
            html_tree = DocumentDetail.html_tree_gen(ph,
                                                     s3_client.meta.endpoint_url + "/" + settings.AWS_STORAGE_BUCKET_NAME + "/")
            context = {
                'filelist': html_tree
            }
        except Exception as e:
            import sys, os
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print ("===========================")
            print(exc_type, fname, exc_tb.tb_lineno)
            print ("===========================")
            response_data = {
                'error': True,
                'message': 'Something went wrong. Please try again.'
            }
            context = {
                'filelist': ""
            }
        return context

    def html_tree_gen(ph, endpoint_url):
        try:
            html_str = "<ul>"
            for li in ph:
                if 'text' in li and 'items' in li:
                    html_str += "<li style='font-weight:bold'>" + str(li['text']) + "/</li>"
                elif 'text' in li and 'spriteCssClass' in li:
                    if li['spriteCssClass'] == 'file' or li['spriteCssClass'] == 'image':
                        html_str += "<li><a href='" + endpoint_url + li['path'] + "' target='_blank' >" + str(
                            li['text']) + "</a></li>"
                    else:
                        html_str += "<li>" + str(li['text']) + "</li>"
                if 'items' in li:
                    html_str += DocumentDetail.html_tree_gen(li['items'], endpoint_url)
            html_str += "</ul>"
            return html_str
        except Exception as e:
            import sys, os
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            return exc_type, fname, exc_tb.tb_lineno

    def buildTree(list, parent_id='root'):
        branch = []
        for li in list:
            if li['parent_id'] == parent_id:
                items = DocumentDetail.buildTree(list, li['text'])
                if items:
                    li['items'] = items
                branch.append(li)
        return branch
