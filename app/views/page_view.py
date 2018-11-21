import json
import os
import time
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import generic
from django.db import transaction
from app.models import PageContent, Questions, Elements, Events, EmailTemplates, Option, ElementsAnswers, CustomClasses, \
    PageContentClasses, PresetEvent, ElementPresetLang, ElementDefaultLang, RuleSet, PagePermission, Tag, Session, \
    EmailContents, PluginSubmitButton, MessageContents, \
    ElementsQuestions, Group, Room, MenuItem, PhotoGroup, ElementHtml, Presets, Rebates, StyleSheet, ExportRule, \
    PluginPdfButton, Setting

from django.db.models import Q
from app.views.file_view import FileView
from app.views.gbhelper.editor_helper import EditorHelper
from app.views.gbhelper.error_report_helper import ErrorR
from publicfront.views.lang_key import LanguageKey

from .common_views import GroupView,CommonContext, EventView
from django.http import Http404
import boto
from boto.s3.key import Key
from django.conf import settings
import datetime
import hashlib
import io
from boto3.session import Session as boto_session
import re
from slugify import slugify
from app.views.language_view import LanguageView
from app.views.cms_view import CmsPageView


class PageView(generic.DetailView):
    def get(self, request):
        if EventView.check_read_permissions(request, 'page_permission'):
            staticPages = PageContent.objects.filter(event_id=request.session['event_auth_user']['event_id'], is_show=1)
            templates = EmailTemplates.objects.filter(event_id=request.session['event_auth_user']['event_id'], is_show=1,
                                                      category='web_pages')
            ErrorR.okgreen(request.session['event_auth_user'])
            context = {
                'staticPages': staticPages,
                'templates': templates,
                'base_url': request.session['event_auth_user']['base_url'],
            }
            if os.environ['ENVIRONMENT_TYPE'] == 'development':
                context["development"]=True
            else:
                context["development"] = False

            filter_context= CommonContext.get_filter_context(request)
            context.update(filter_context)
            return render(request, 'page/pages.html', context)

    def urlify(s):
        s = re.sub(r"[^\w\s]", '_', s)
        s = re.sub(r"\s+", '_', s)
        return s

    @staticmethod
    def add(request):
        return render(request, 'page/add_page.html')

    @transaction.atomic
    def post(self, request):

        try:
            response_data = {}
            admin_id = request.session['event_auth_user']['id']
            if 'id' in request.POST:
                page_id = request.POST.get('id')
                if 'content' in request.POST:
                    # get css version
                    css_version_obj = StyleSheet.objects.get(event_id=request.session['event_auth_user']['event_id'])
                    css_version = css_version_obj.version

                    data = json.loads(request.POST.get('content'))
                    filter = request.POST.get('filter_list')
                    element_filter = request.POST.get('element_filters')
                    content = data['content']
                    # For Wsit S3
                    content = content.replace('[[file]]', "[[static]]public/[[event_url]]/files")
                    content = content.replace('[[files]]', "[[static]]public/[[event_url]]/files/")
                    content = content.replace('[[css]]', "[[static]]public/[[event_url]]/compiled_css/style.css?v="+str(css_version))

                    # For Wsit Event
                    # content = content.replace('[[file]]', "[[static]]public/files")
                    # content = content.replace('[[files]]', "[[static]]public/files/")
                    # content = content.replace('[[css]]',
                    #                           "[[static]]public/compiled_css/main_style.css?v=" + str(
                    #                               css_version))

                    content = content.replace(settings.STATIC_URL_ALT, '[[static]]')
                    content = content.replace(settings.STATIC_URL_ALT + 'public/', '[[parmanent]]')
                    old_page = PageContent.objects.get(id=page_id)
                    if old_page.element_filter != None and old_page.element_filter != '':
                        old_element_filter = json.loads(old_page.element_filter)
                        new_element_filter = json.loads(request.POST.get('element_filters'))
                        for element in old_element_filter:
                            element_box_id = element['box_id'].split('-')[1]
                            old_element_exist = PageView.in_dictlist('box_id', element['box_id'], new_element_filter)
                            if old_element_exist == 0:
                                ElementsAnswers.objects.filter(page_id=page_id, box_id=element_box_id,
                                                               element_question__group_id=int(
                                                                   element['element_id'])).delete()
                    PageContent.objects.filter(id=page_id).update(content=content, last_updated_by_id=admin_id,
                                                                  filter=filter, element_filter=element_filter)
                    page = PageContent.objects.get(id=page_id)
                    response_data = {
                        'success': True,
                        'message': 'Page Content Updated',
                        'page': page.as_dict()
                    }
                else:
                    groups = json.loads(request.POST.get('group_id'))
                    page_url = request.POST.get('page_url')
                    if not PageView.page_url_exist(request, page_url):
                        page_template = request.POST.get('page_template')
                        is_login_required = request.POST.get('is_login_required')
                        login_required = False
                        is_disallow_logged_in = request.POST.get('disallow_logged_in')
                        disallow_logged_in = False
                        if is_login_required == 'true':
                            login_required = True
                        if is_disallow_logged_in == 'true':
                            disallow_logged_in = True
                        old_page = PageContent.objects.get(id=page_id)
                        if old_page.url == 'start':
                            page_url = 'start'
                        elif old_page.url == 'logged-in':
                            page_url = 'logged-in'
                        elif old_page.url == 'logout':
                            page_url = 'logout'
                        url = PageContent.objects.filter(url=page_url,
                                                         event_id=request.session['event_auth_user'][
                                                             'event_id']).exclude(
                            id=page_id)
                        if not url.exists():
                            PageContent.objects.filter(id=page_id).update(url=page_url, template_id=page_template,
                                                                          login_required=login_required,disallow_logged_in=disallow_logged_in,last_updated_by_id=admin_id)

                            page = PageContent.objects.get(id=page_id)
                            MenuItem.objects.filter(content_id=page.id).update(url=page.url)
                            response_data = {
                                'success': True,
                                'message': 'Page Content Updated',
                                'page': page.as_dict()
                            }
                            PagePermission.objects.filter(page_id=page_id).delete()
                            if groups:
                                for group in groups:
                                    permission = PagePermission(page_id=page_id, rule_id=group)
                                    permission.save()
                        else:
                            response_data = {
                                'error': True,
                                'message': 'Page Url already Exist'
                            }
                    else:
                        response_data = {
                            'warning': True,
                            'message': 'Page Url already Exist'
                        }

            else:
                groups = json.loads(request.POST.get('group_id'))
                page_url = request.POST.get('page_url')
                if not PageView.page_url_exist(request, page_url):
                    page_template = request.POST.get('page_template')
                    is_login_required = request.POST.get('is_login_required')
                    login_required = False
                    if is_login_required == 'true':
                        login_required = True
                    is_disallow_logged_in = request.POST.get('disallow_logged_in')
                    disallow_logged_in = False
                    if is_disallow_logged_in == 'true':
                        dissallow_logged_in = True
                    url = PageContent.objects.filter(url=page_url,
                                                     event_id=request.session['event_auth_user']['event_id'])
                    if not url.exists():
                        page_content = PageContent(url=page_url, login_required=login_required, disallow_logged_in=disallow_logged_in, created_by_id=admin_id,
                                                   last_updated_by_id=admin_id, template_id=page_template,
                                                   event_id=request.session['event_auth_user']['event_id'])
                        page_content.save()
                        if groups:
                            for group in groups:
                                permission = PagePermission(page_id=page_content.id, rule_id=group)
                                permission.save()
                        response_data = {
                            'success': True,
                            'message': 'Page content created',
                            'page': page_content.as_dict()
                        }
                    else:
                        response_data = {
                            'error': True,
                            'message': 'Page Url already Exist'
                        }
                else:
                    response_data = {
                        'warning': True,
                        'message': 'Page Url already Exist'
                    }

            return HttpResponse(json.dumps(response_data), content_type="application/json")

        except Exception as e:
            ErrorR.efail(e)
            response_data = {
                'error': True,
                'message': 'Something went wrong. Please try again.'
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    def page_url_exist(request, name):
        from django.core.urlresolvers import reverse
        try:
            reverse(name, kwargs={'event_url': request.session['event_auth_user']['event_url']})
            return True
        except Exception:
            return False

    def in_dictlist(k, value, my_dictlist):
        for this in my_dictlist:
            if this[k] == value:
                return 1
        return 0

    def delete(request):
        response_data = {}
        if EventView.check_permissions(request, 'page_permission'):
            page_id = request.POST.get('id')
            page = PageContent.objects.get(id=page_id)
            default_pages = ['start', 'logged-in', 'default-login-page', 'request-login-page', 'reset-password-page',
                             'new-password-page', 'messages', 'logout', 'payment-success', 'payment-cancel', '403-forbidden-registered', '403-forbidden-unregistered', '404-not-found']
            if page.url in default_pages:
                response_data['warning'] = "You can't delete the " + str(page.url) + " page"
            else:
                page_url = page.url+'-deleted-'+str(page.id)
                PageContent.objects.filter(id=page_id).update(is_show=0,url=page_url)
                response_data['success'] = "Page Deleted Successfully"
        else:
            response_data['error'] = "You do not have Permission to do this"
        return HttpResponse(json.dumps(response_data), content_type="application/json")


    @staticmethod
    def upload_image(request):
        image = request.FILES['files']
        # hash_object = hashlib.md5(str(datetime.datetime.now()).encode('utf-8'))
        # filename = hash_object.hexdigest()
        response = {}
        filename = PageView.urlify(image.name.split('.')[0])

        event_id = request.session['event_auth_user']['event_id']
        event = Events.objects.get(pk=event_id)
        event_url = event.url

        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, host=settings.AWS_STORAGE_HOST)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        extension = image.content_type.split('image/')[1]
        key_name = 'public/' + event_url + '/files/page_images/' + filename + '.' + extension
        k = Key(bucket)
        k.key = key_name

        if not k.exists():
            key = bucket.new_key(key_name)
            key.set_contents_from_string(image.read())
            key.set_metadata('Content-Type', 'image/' + image.content_type)
            key.set_acl('public-read')
            key.make_public()
            response['success'] = True
            response['msg'] = "Successfully Uploaded"
        else:
            # k.set_contents_from_string(image.read())
            # k.set_metadata('Content-Type', 'image/' + image.content_type)
            # k.set_acl('public-read')
            # k.make_public()
            response['success'] = False
            response['msg'] = "File name already exists"

        return HttpResponse(json.dumps(response), content_type="application/json")

    def set_element_settings(request):
        try:
            response = {}
            admin_id = request.session['event_auth_user']['id']
            page_id = request.POST.get('page_id')
            box_id = request.POST.get('box_id')
            language_id = request.POST.get('language_id')

            element_settings = json.loads(request.POST.get('element_settings'))
            response['message'] = 'all settings are updated'
            element_settings_dict = []
            element_settings_title_dict = []
            for setting in element_settings:
                setting_form_data = {
                    "page_id": page_id,
                    "box_id": box_id,
                    "element_question_id": setting['setting_id'],
                    "last_updated_by_id": admin_id
                }
                if setting['setting_answer'] == None:
                    setting['setting_answer'] = ""

                alreadySavedSetting = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id, element_question_id=setting['setting_id'])

                if alreadySavedSetting.exists():
                    if setting['type'] == 'message':
                        if setting['setting_answer'] != "":
                            # print(setting['setting_answer'])
                            # obj = {}
                            # obj[str(language_id)] = setting['setting_answer']
                            # print(str(obj).replace("'",'"'))
                            if alreadySavedSetting[0].description != '':
                                obj = json.loads(alreadySavedSetting[0].description,strict=False)
                                obj[str(language_id)]=setting['setting_answer']
                                setting_form_data['description'] =  str(obj).replace("'",'"')
                                # setting_form_data['description'] =  str(obj)
                                # import ast
                                # print(ast.literal_eval(setting_form_data['description']))
                            else:
                                obj = {}
                                obj[str(language_id)]=setting['setting_answer']
                                setting_form_data['description'] = str(obj).replace("'",'"')
                                # setting_form_data['description'] = str(obj)
                        # else:
                        #     if alreadySavedSetting[0].description != '':
                        #         obj = json.loads(alreadySavedSetting[0].description,strict=False)
                        #         obj[str(language_id)]=setting['setting_answer']
                        #         setting_form_data['description'] =  str(obj).replace("'",'"')
                        #     else:
                        #         obj = {}
                        #         obj[str(language_id)]=setting['setting_answer']
                        #         setting_form_data['description'] = str(obj).replace("'",'"')

                    elif int(setting['setting_id']) == 69 or int(setting['setting_id']) == 343:
                        if setting['setting_answer'] != "":
                            if alreadySavedSetting[0].answer != '':
                                try:
                                    obj = json.loads(alreadySavedSetting[0].answer,strict=False)
                                    obj[str(language_id)]=setting['setting_answer']
                                    setting_form_data['answer'] =  str(obj).replace("'",'"')
                                except:
                                    obj = {}
                                    obj[str(language_id)]=setting['setting_answer']
                                    setting_form_data['answer'] =  str(obj).replace("'",'"')
                            else:
                                obj = {}
                                obj[str(language_id)]=setting['setting_answer']
                                setting_form_data['answer'] = str(obj).replace("'",'"')
                    else:
                        setting_form_data['answer'] = setting['setting_answer']
                    ElementsAnswers.objects.filter(id=alreadySavedSetting[0].id).update(**setting_form_data)
                    response['success'] = True
                    settings_data = alreadySavedSetting[0]
                    # if settings_data.description != "":
                    #     msg = json.loads(settings_data.description,strict=False)
                    #     settings_data.description = msg[str(language_id)]
                    # if settings_data.element_question.question_key == "submit_button_title":
                    #     title = json.loads(settings_data.answer,strict=False)
                    #     settings_data.answer = title[str(language_id)]
                    # if settings_data.element_question.question_key == "pdf_button_title":
                    #     title = json.loads(settings_data.answer, strict=False)
                    #     settings_data.answer = title[str(language_id)]
                    setting_dict = {
                        'answer': setting_form_data['answer'],
                        'box_id': settings_data.box_id,
                        'element_question': {
                            "id": settings_data.element_question.id,
                            "group_slug": settings_data.element_question.group.slug,
                            "question_key": settings_data.element_question.question_key
                        }
                    }
                    if settings_data.element_question.question_key == "submit_button_title" or settings_data.element_question.question_key == "pdf_button_title":
                        title = json.loads(settings_data.answer, strict=False)
                        settings_data.answer = title[str(language_id)]
                        setting_dict['answer'] = settings_data.answer
                        element_settings_title_dict.append(setting_dict)
                    else:
                        element_settings_dict.append(setting_dict)
                else:
                    setting_form_data['page_id'] = page_id
                    setting_form_data['box_id'] = box_id
                    setting_form_data['element_question_id'] = setting['setting_id']
                    setting_form_data['created_by_id'] = admin_id
                    if setting['type'] == 'message':
                        obj = {}
                        obj[str(language_id)]=setting['setting_answer']
                        setting_form_data['description'] = str(obj).replace("'",'"')
                    elif int(setting['setting_id']) == 69 or int(setting['setting_id']) == 343:
                        obj = {}
                        obj[str(language_id)]=setting['setting_answer']
                        setting_form_data['answer'] = str(obj).replace("'",'"')
                    else:
                        setting_form_data['answer'] = setting['setting_answer']
                    new_message = ElementsAnswers(**setting_form_data)
                    new_message.save()
                    response['success'] = True
                    # settings_data = ElementsAnswers.objects.get(id=new_message.id)
                    settings_data = new_message
                    # if settings_data.description != "":
                    #     msg = json.loads(settings_data.description,strict=False)
                    #     settings_data.description = msg[str(language_id)]
                    # if settings_data.element_question.question_key == "submit_button_title":
                    #     title = json.loads(settings_data.answer,strict=False)
                    #     settings_data.answer = title[str(language_id)]
                    # if settings_data.element_question.question_key == "pdf_button_title":
                    #     title = json.loads(settings_data.answer, strict=False)
                    #     settings_data.answer = title[str(language_id)]
                    # element_settings_dict.append(settings_data.as_dict())
                    setting_dict = {
                        'answer': settings_data.answer,
                        'box_id': settings_data.box_id,
                        'element_question': {
                            "id": settings_data.element_question.id,
                            "group_slug": settings_data.element_question.group.slug,
                            "question_key": settings_data.element_question.question_key
                        }
                    }
                    if settings_data.element_question.question_key == "submit_button_title" or settings_data.element_question.question_key == "pdf_button_title":
                        title = json.loads(settings_data.answer, strict=False)
                        settings_data.answer = title[str(language_id)]
                        setting_dict['answer'] = settings_data.answer
                        element_settings_title_dict.append(setting_dict)
                    else:
                        element_settings_dict.append(setting_dict)
            response['element_settings'] = element_settings_dict
            response['element_title_settings'] = element_settings_title_dict
            if 'photo_group_name' in request.POST:
                photo_group_name =  request.POST.get('photo_group_name').strip()
                photo_group_id =  request.POST.get('photo_group_id')
                if photo_group_id != '':
                    if PhotoGroup.objects.filter(name=photo_group_name,page__event_id=request.session['event_auth_user']['event_id']).exclude(id=photo_group_id).exists():
                        photo_group_name = str(photo_group_name) + '-1'
                    PhotoGroup.objects.filter(id=photo_group_id).update(name=photo_group_name)

        except Exception as e:
            ErrorR.efail(e)
            response = {
                'error': True,
                'message': 'Something went wrong. Please try again.'
            }
        return HttpResponse(json.dumps(response), content_type="application/json")

    def get_element_settings(request):
        response = {}
        page_id = request.POST.get('page_id')
        box_id = request.POST.get('box_id')
        language_id = request.POST.get('language_id')
        element_settings = []
        message = ''
        settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id).select_related('element_question')
        for setting in settings:
            if setting.description != '':
                try:
                    description = json.loads(setting.description,strict=False)
                    if description[str(language_id)]:
                        message = description[str(language_id)]
                except Exception as e:
                    ErrorR.efail(e)
                    try:
                        current_language = LanguageView.get_current_preset(request)
                        description = json.loads(setting.description,strict=False)
                        if description[str(current_language.preset_id)]:
                            message = description[str(current_language.preset_id)]
                    except:
                        pass

            elif setting.element_question.question_key == "attendee_list_selected_columns":
                try:
                    setting_data = json.loads(setting.answer)
                    questionGroup = GroupView.get_questionGroup(request)
                    question_groups = []
                    folder_index = 0
                    for group in questionGroup:
                        group_dict = {}
                        group_dict['text'] = group.name.title()
                        group_dict['spriteCssClass'] = "folder"
                        group_dict['gp_data_id'] = group.id
                        group_dict['index'] = setting_data['group'][str(group.id)]['index']
                        group_dict['checked'] = setting_data['group'][str(group.id)]['checked']
                        folder_index += 1
                        questions = []
                        group.questions = Questions.objects.all().filter(group_id=group.id).order_by('question_order')
                        group.column_questions = group.questions
                        for question in group.questions:
                            question_dict = {}
                            question_dict['text'] = question.title.title()
                            question_dict['spriteCssClass'] = "question file"
                            question_dict['data_id'] = question.id
                            if str(question.id) in setting_data['question']:
                                question_dict['index'] = setting_data['question'][str(question.id)]['index']
                                question_dict['checked'] = setting_data['question'][str(question.id)]['checked']
                            questions.append(question_dict)
                        group_dict['items'] = questions
                        question_groups.append(group_dict)
                    if len(question_groups) > 0:
                        question_groups[0]['expanded'] = True
                    response['question_groups'] = json.dumps(question_groups)
                    setting_dict = {
                        "id": setting.id,
                        "element_question": {
                            "id": setting.element_question.id,
                            "question_key": setting.element_question.question_key
                        },
                        "answer": setting.answer
                    }
                    # element_settings.append(setting.as_dict())
                    element_settings.append(setting_dict)
                except Exception as e:
                    ErrorR.efail(e)
            elif setting.element_question.question_key == "submit_button_title" or setting.element_question.question_key == "pdf_button_title":
                title_new = ''
                if setting.answer != '':
                    try:
                        title = json.loads(setting.answer,strict=False)
                        if title[str(language_id)]:
                            title_new = title[str(language_id)]
                    except ValueError:
                        title_new = setting.answer
                    except Exception as e:
                        ErrorR.okblue(type(e).__name__)
                        try:
                            current_language = LanguageView.get_current_preset(request)
                            title = json.loads(setting.answer,strict=False)
                            if title[str(current_language.preset_id)]:
                                title_new = title[str(current_language.preset_id)]
                        except:
                            pass
                # button_setting = setting.as_dict()
                button_setting = {
                    "id": setting.id,
                    "element_question": {
                        "id": setting.element_question.id,
                        "question_key": setting.element_question.question_key
                    },
                    "answer": setting.answer
                }
                button_setting['answer'] = title_new
                element_settings.append(button_setting)
            else:
                setting_dict = {
                    "id": setting.id,
                    "element_question": {
                        "id": setting.element_question.id,
                        "question_key": setting.element_question.question_key
                    },
                    "answer": setting.answer
                }
                element_settings.append(setting_dict)
                # element_settings.append(setting.as_dict())
        response['element_settings'] = element_settings
        response['message_setting'] = message
        response['success'] = True
        return HttpResponse(json.dumps(response), content_type="application/json")

    def get_custom_classes(request):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        # val = request.POST.get('q')
        # custom_classes = CustomClasses.objects.values('classname', 'id').filter(classname__startswith=val)
        custom_classes = CustomClasses.objects.values('classname', 'id').filter(event_id=event_id)
        my_data = []
        for custom_class in custom_classes:
            arr_data = {
                'id': custom_class['id'],
                'text': custom_class['classname']
            }
            my_data.append(arr_data)
        response_data['results'] = my_data
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def set_custom_classes(request):
        page_id = request.POST.get('page_id')
        box_id = request.POST.get('box_id')
        box_classes = json.loads(request.POST.get('box_classes'))
        admin_id = request.session['event_auth_user']['id']
        class_exist = []
        response = {}
        event_id = request.session['event_auth_user']['event_id']
        for box_class in box_classes:
            if 'id' in box_class and box_class['id'].isdigit():
                class_exist.append(box_class['id'])
                if not (
                        PageContentClasses.objects.filter(page_id=page_id, box_id=box_id,
                                                          classname_id=box_class['id']).exists()):
                    page_box_class = PageContentClasses(page_id=page_id, box_id=box_id, classname_id=box_class['id'])
                    page_box_class.save()
            # if box_class.isdigit():
            #     class_exist.append(box_class)
            #     if not (
            #     PageContentClasses.objects.filter(page_id=page_id, box_id=box_id, classname_id=box_class).exists()):
            #         page_box_class = PageContentClasses(page_id=page_id, box_id=box_id, classname_id=box_class)
            #         page_box_class.save()
            else:
                new_class = CustomClasses(classname=box_class['text'], created_by_id=admin_id, event_id=event_id)
                new_class.save()
                page_box_class = PageContentClasses(page_id=page_id, box_id=box_id, classname_id=new_class.id)
                page_box_class.save()
                class_exist.append(new_class.id)
                # new_class = CustomClasses(classname=box_class, created_by_id=admin_id)
                # new_class.save()
                # page_box_class = PageContentClasses(page_id=page_id, box_id=box_id, classname_id=new_class.id)
                # page_box_class.save()
                # class_exist.append(new_class.id)
        deleted_class = PageContentClasses.objects.filter(page_id=page_id, box_id=box_id).exclude(
            classname_id__in=class_exist)
        for page_class in deleted_class:
            page_class.delete()
        if "filter_list" in request.POST:
            filter_list = request.POST.get('filter_list')
            PageContent.objects.filter(id=page_id).update(filter=filter_list)
        page = PageContent.objects.get(id=page_id)
        response['message'] = 'Custom classes are updated'
        response['page'] = page.as_dict()
        return HttpResponse(json.dumps(response), content_type="application/json")

    def get_box_classes(request):
        page_id = request.POST.get('page_id')
        box_id = request.POST.get('box_id')
        class_list = []
        box_classes = PageContentClasses.objects.filter(page_id=page_id, box_id=box_id)
        for box_class in box_classes:
            class_list.append(box_class.as_dict())
        context = {
            "class_list": class_list
        }
        return HttpResponse(json.dumps(context), content_type="application/json")

    def get_submit_button_name(request):
        page_id = request.POST.get('page_id')
        admin_id = request.session['event_auth_user']['id']
        name = ''
        page = PageContent.objects.get(id=page_id)
        page_buttons = PluginSubmitButton.objects.filter(page_id=page_id).order_by('-id')
        if len(page_buttons) == 0:
            name = page.url + '-button'
        else:
            btn_no_array = page_buttons[0].name.split('-')
            try:
                btn_no = int(btn_no_array[len(btn_no_array) - 1])
                name = page.url + '-button-' + str(btn_no + 1)
            except Exception:
                name = page.url + '-button-2'

        submit_button = PluginSubmitButton(
            name=name,
            page_id=page_id,
            created_by_id=admin_id
        )
        submit_button.save()
        context = {
            "submit_button": submit_button.as_dict()
        }
        return HttpResponse(json.dumps(context), content_type="application/json")

    def get_pdf_button_name(request):
        page_id = request.POST.get('page_id')
        admin_id = request.session['event_auth_user']['id']
        name = ''
        page = PageContent.objects.get(id=page_id)
        page_pdf_buttons = PluginPdfButton.objects.filter(page_id=page_id).order_by('-id')
        if len(page_pdf_buttons) == 0:
            name = page.url + '-pdf-button'
        else:
            btn_no_array = page_pdf_buttons[0].name.split('-')
            try:
                btn_no = int(btn_no_array[len(btn_no_array) - 1])
                name = page.url + '-pdf-button-' + str(btn_no + 1)
            except Exception:
                name = page.url + '-pdf-button-2'

        pdf_button = PluginPdfButton(
            name=name,
            page_id=page_id,
            created_by_id=admin_id
        )
        pdf_button.save()
        context = {
            "pdf_button": pdf_button.as_dict()
        }
        return HttpResponse(json.dumps(context), content_type="application/json")

    def get_photo_group_name(request):
        page_id = request.POST.get('page_id')
        admin_id = request.session['event_auth_user']['id']
        name = ''
        page = PageContent.objects.get(id=page_id)
        page_photo_groups = PhotoGroup.objects.filter(page_id=page_id).order_by('-id')
        if len(page_photo_groups) == 0:
            name = page.url + '-photo-group'
        else:
            group_no_array = page_photo_groups[0].name.split('-')
            try:
                group_no = int(group_no_array[len(group_no_array) - 1])
                name = page.url + '-photo-group-' + str(group_no + 1)
            except Exception:
                name = page.url + '-photo-group-2'

        photo_group = PhotoGroup(
            name=name,
            page_id=page_id,
            created_by_id=admin_id
        )
        photo_group.save()
        context = {
            "photo_group": photo_group.as_dict()
        }
        return HttpResponse(json.dumps(context), content_type="application/json")

    def get_element_html(request):
        response = {}
        try:
            page_id = request.POST.get('page_id')
            box_id = request.POST.get('box_id')
            language_id = request.POST.get('language_id')
            element_html = ElementHtml.objects.filter(page_id=page_id, box_id=box_id,language_id=language_id).first()
            if not element_html:
                current_language = LanguageView.get_current_preset(request)
                if current_language != None:
                    element_html = ElementHtml.objects.filter(page_id=page_id, box_id=box_id,language_id=current_language.preset_id).first()
                else:
                    element_html = ElementHtml.objects.filter(page_id=page_id, box_id=box_id,language_id=6).first()
            if element_html:
                element = element_html.as_dict()
            else:
                element = ""
            response['success'] = True
            response['element_html'] = element
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return HttpResponse(json.dumps(response), content_type="application/json")

    def delete_element_html(request):
        response = {}
        try:
            page_id = request.POST.get('page_id')
            box_id = request.POST.get('box_id')
            ElementHtml.objects.filter(page_id=page_id, box_id=box_id).delete()
            response['success'] = True
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return HttpResponse(json.dumps(response), content_type="application/json")

    def set_element_html(request):
        response = {}
        try:
            page_id = request.POST.get('page_id')
            box_id = request.POST.get('box_id')
            language_id = request.POST.get('language_id')
            html_form = {
                "page_id": page_id,
                "box_id" : box_id,
                "compiled" : request.POST.get('compiled_html'),
                "uncompiled" : request.POST.get('uncompiled_html'),
                "language_id":language_id,
                "created_by_id" : request.session["event_auth_user"]["id"]
            }
            if ElementHtml.objects.filter(page_id=page_id, box_id=box_id,language_id=language_id).exists():
                ElementHtml.objects.filter(page_id=page_id, box_id=box_id,language_id=language_id).update(**html_form)
            else:
                element_html = ElementHtml(**html_form)
                element_html.save()
            response['success'] = True
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return HttpResponse(json.dumps(response), content_type="application/json")


    def get_sessions_by_groups(request):
        response_data = {}
        my_data = []
        groups = json.loads(request.POST.get('groups'))
        sessions = Session.objects.filter(group_id__in=groups, group__is_show=1,
                                          group__event_id=request.session['event_auth_user']['event_id'])
        for session in sessions:
            arr_data = {'id': session.id, 'text': str(session.name)}
            my_data.append(arr_data)
        response_data['results'] = my_data
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_all_rebates(request):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        rebates = Rebates.objects.filter(event_id=event_id).values('name', 'id')
        my_data = []
        for rebate in rebates:
            arr_data = {
                'id': rebate['id'],
                'text': rebate['name']
            }
            my_data.append(arr_data)
        response_data['results'] = my_data
        return HttpResponse(json.dumps(response_data), content_type="application/json")


class PageDetailView(generic.DetailView):
    @staticmethod
    def get_uploaded_images(request):
        event_id = request.session['event_auth_user']['event_id']
        event = Events.objects.get(pk=event_id)
        event_url = event.url
        session = boto_session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                               region_name='eu-west-1')
        s3_client = session.client('s3')
        s3_response = s3_client.list_objects(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Prefix='public/' + event_url + '/files/page_images'
        )
        response = {}
        if 'Contents' in s3_response:
            files = s3_response['Contents']
            page_images = []
            for file in files:
                key = file['Key']
                url = '{}/{}/{}'.format(s3_client.meta.endpoint_url, settings.AWS_STORAGE_BUCKET_NAME, key)
                page_images.append({
                    'key': key,
                    'url': url
                })
            response = {
                'data': page_images
            }
        return HttpResponse(json.dumps(response), content_type='application/json')

    def get_editor_all_uploaded_images(request):
        event_id = request.session['event_auth_user']['event_id']
        event = Events.objects.get(pk=event_id)
        event_url = event.url
        session = boto_session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                               region_name='eu-west-1')
        s3_client = session.client('s3')
        s3_response = s3_client.list_objects(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Prefix='public/' + event_url + '/files'
        )
        # response = {}
        if 'Contents' in s3_response:
            files = s3_response['Contents']
            page_images = []
            for file in files:
                key = file['Key']
                url = '{}/{}/{}'.format(s3_client.meta.endpoint_url, settings.AWS_STORAGE_BUCKET_NAME, key)
                file_type_array = key.split(".")
                file_type = file_type_array[len(file_type_array)-1]
                if file_type.lower() == "png" or file_type.lower() == "jpeg" or file_type.lower() == "jpg"  or file_type.lower() == "svg":
                    page_images.append({
                        "url": url,
                        "thumb": url
                    })
        return HttpResponse(json.dumps(page_images), content_type='application/json')

    def upload_image_from_editor(request):
        file = request.FILES['image_param']
        event_url = request.session['event_auth_user']['event_url']
        response = {}
        filename = FileView.urlify(file.name.split('.')[0])
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, host=settings.AWS_STORAGE_HOST)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        extension = file.content_type.split('image/')[1]
        key_name = 'public/' + event_url + '/files/page_images/' + filename + '.' + extension
        contentType = file.content_type

        k = Key(bucket)
        k.key = key_name

        if not k.exists():
            key = bucket.new_key(key_name)
            key.set_metadata('Content-Type', contentType)
            key.set_contents_from_string(file.read())
            key.set_acl('public-read')
            key.make_public()
            # response['success'] = True
            # response['msg'] = "Successfully Uploaded"
        else:
            key = bucket.new_key(key_name)
            key.set_metadata('Content-Type', contentType)
            key.set_contents_from_string(file.read())
            key.set_acl('public-read')
            key.make_public()
            # response['success'] = True
            # response['msg'] = "Successfully Uploaded"

        key_detail = bucket.get_key(key_name)
        key_url = key_detail.generate_url(0, query_auth=False)
        response["link"] = key_url

        return HttpResponse(json.dumps(response), content_type="application/json")

    def delete_image_from_editor(request):
        response = {}
        try:
            key_src = request.POST.get('src')
            print(key_src)
            conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, host=settings.AWS_STORAGE_HOST)
            bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
            # key = bucket.get_key(key_src)
            get_key = key_src.split('public')
            key = 'public'+get_key[1]
            print(key)
            bucket.delete_key(key)
            response['success'] = True
            response['message'] = 'Deleted successfully'
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
            response['message'] = 'Something went wrong. please try again'
        return HttpResponse(json.dumps(response), content_type="application/json")

    def get_object(self, pk):
        try:
            page = PageContent.objects.filter(id=pk,template__event_id=self.request.session['event_auth_user']['event_id'])
            if page.exists():
                return page[0]
            else:
                raise Http404
        except PageContent.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        if EventView.check_permissions(request, 'page_permission'):
            static_page = self.get_object(pk)
            pageContent = PageDetailView.get_page_content(static_page, request)
            try:
                current_language = PresetEvent.objects.filter(event_id=request.session['event_auth_user']['event_id']).first()
                language_id = current_language.preset.id
            except:
                current_language = Presets.objects.get(id=6)
                language_id = current_language.preset.id
            if static_page.template_id == 1:
                content = pageContent.replace('[[static_alt]]', settings.STATIC_URL_ALT)

                context = {
                    "content": content,
                    "static_page": static_page
                }
                return render(request, 'public/static_pages/page.html', context)
            else:
                new_time = time.time()
                template = EmailTemplates.objects.get(id=static_page.template_id)
                # content = pageContent.replace('[[static]]', settings.STATIC_URL_ALT)
                css_version_obj = StyleSheet.objects.get(event_id=request.session['event_auth_user']['event_id'])
                css_version = css_version_obj.version

                page_content = template.content.replace('{content}', "<div id='content'>"+pageContent+"</div>")
                # For Wsit S3
                page_content = page_content.replace('[[file]]', "[[static]]public/[[event_url]]/files")
                page_content = page_content.replace('[[files]]', "[[static]]public/[[event_url]]/files/")
                page_content = page_content.replace('[[css]]', "[[static]]public/[[event_url]]/compiled_css/style.css?v="+str(css_version))

                # For Wsit Event
                # page_content = page_content.replace('[[file]]', "[[static]]public/files")
                # page_content = page_content.replace('[[files]]', "[[static]]public/files/")
                # page_content = page_content.replace('[[css]]',
                #                                     "[[static]]public/compiled_css/main_style.css?v=" + str(
                #                                         css_version))

                page_content = page_content.replace('[[static]]', settings.STATIC_URL_ALT)
                if '{menu}' in page_content:
                    first_level_menu = MenuItem.objects.filter(level=1, event_id=static_page.template.event_id).order_by("rank")
                    all_menus = PageDetailView.get_all_menu(request,first_level_menu, language_id)
                    menu = render_to_string('content/cms_menu_head.html',{"all_menu": all_menus})
                    page_content = page_content.replace('{menu}', menu)
                if '{language}' in page_content:
                    language = PageDetailView.get_all_language(request)
                    page_content = page_content.replace('{language}', language)
                page_content = page_content.replace('[[event_url]]', static_page.template.event.url)
                page_content = page_content.replace('[[parmanent]]', settings.STATIC_URL_ALT + 'public/')
                context = {
                    "page_content": page_content
                }
                return render(request, 'page/page_with_template.html', context)
        else:
            raise Http404

    def get_page_content(static_page, request):
        event_id = request.session['event_auth_user']['event_id']
        question_groups = PageDetailView.get_treeView_question_group(request)
        locationGroups = GroupView.get_locationGroup(request)
        sessionGroups = GroupView.get_sessionGroup(request)
        hotelGroups = GroupView.get_hotelGroup(request)
        for hotel_group in hotelGroups:
            hotel_group.rooms = Room.objects.all().select_related("hotel").filter(hotel__group_id=hotel_group.id).order_by('room_order')
        quick_filter = RuleSet.objects.filter(name='quick-filter',
                                              created_by_id=request.session['event_auth_user']['id'],
                                              group__event_id=event_id)
        quick_filter_id = ''
        if quick_filter.exists():
            quick_filter_id = quick_filter[0].id
        filterGroups = GroupView.get_filterGroup(request)
        filter_groups = []
        quick_filter_dict = {}
        quick_filter_dict['text'] = "Quick Filter"
        quick_filter_dict['spriteCssClass'] = "filter"
        quick_filter_dict['data_type'] = "quick-filter"
        quick_filter_dict['data_id'] = quick_filter_id
        quick_filter_dict['expanded'] = True
        filter_groups.append(quick_filter_dict)
        for group in filterGroups:
            group_filter_dict = {}
            group_filter_dict['text'] = group.name.title()
            group_filter_dict['spriteCssClass'] = "folder"
            group_filter_dict['expanded'] = True
            filters = []
            group.rules = RuleSet.objects.filter(group_id=group.id).order_by('rule_order').exclude(name='quick-filter')
            for rule in group.rules:
                rule_dict = {}
                rule_dict['text'] = rule.name.title()
                rule_dict['spriteCssClass'] = "filter"
                rule_dict['data_type'] = "filter"
                rule_dict['data_id'] = rule.id
                filters.append(rule_dict)
            group_filter_dict['items'] = filters
            filter_groups.append(group_filter_dict)
        current_preset = LanguageView.get_current_preset(request)
        if current_preset != None:
            current_preset = current_preset.preset_id
        presetsEvent = PresetEvent.objects.filter(event_id=event_id)
        language = {}
        modules = Elements.objects.all().exclude(type="public_notification").order_by('name')
        plugins = []
        plugin_category_dict = {}
        plugin_category_dict['text'] = "Plugins"
        plugin_category_dict['spriteCssClass'] = "folder"
        plugin_category_dict['expanded'] = True
        module_data = []
        plugin_settings = {}
        for module in modules:
            plugin_slug = module.slug.replace("-", "_")
            if presetsEvent.exists():
                lang_data = ElementPresetLang.objects.filter(preset_id=presetsEvent[0].preset_id,
                                                             element_default_lang__element_id=module.id)
                lang_key = {}
                for lang in lang_data:
                    lang_key[lang.element_default_lang.lang_key] = lang.value

                language[plugin_slug] = lang_key
            else:
                lang_data = ElementDefaultLang.objects.filter(element_id=module.id)
                lang_key = {}
                for lang in lang_data:
                    lang_key[lang.lang_key] = lang.default_value
                language[plugin_slug] = lang_key
            module_settings = ElementsQuestions.objects.filter(group_id=module.id)
            # module_settings = module.elementsquestions_set.all()
            module_key = {}
            for module_setting in module_settings:
                module_key[module_setting.question_key] = module_setting
            plugin_settings[plugin_slug] = module_key
            if module.type != 'default_plugin':
                module.name = module.name.replace('-', ' ')
                module_dict = {}
                module_dict['text'] = module.name.title()
                module_dict['spriteCssClass'] = "plugin"
                module_dict['data_id'] = module.id
                module_data.append(module_dict)
                plugin_category_dict['items'] = module_data
        plugins.append(plugin_category_dict)
        content = LanguageElement.replace_page_content(request,static_page,current_preset)
        questionGroups = GroupView.get_questionGroup(request)
        for question_group in questionGroups:
            question_group.questions = Questions.objects.filter(group_id=question_group.id)
            for question in question_group.questions:
                if question.type != 'text' and question.type != 'textarea':
                    question.options = Option.objects.filter(question_id=question.id)
        tags = Tag.objects.filter(event_id=event_id)
        attendee_groups = GroupView.get_attendeeGroup(request)
        session_groups = GroupView.get_sessionGroup(request)
        for group in session_groups:
            group.sessions = Session.objects.all().filter(group_id=group.id)
        element_settings_dict = LanguageElement.get_element_settings_data(request,static_page,current_preset)
        element_settings_title_dict = LanguageElement.get_element_title_settings_data(request,static_page,current_preset)
        class_list = LanguageElement.get_page_classes(request,static_page)
        all_pages = PageContent.objects.filter(event_id=event_id)
        event_id = request.session['event_auth_user']['event_id']
        emails = EmailContents.objects.filter(template__event_id=event_id, is_show=1)
        messages = MessageContents.objects.filter(event_id=event_id, is_show=1)
        pages = PageContent.objects.filter(event_id=event_id)
        for page in pages:
            page.buttons = PluginSubmitButton.objects.filter(page_id=page.id)
        exclude_form_pages = ['attendee-details-page', 'session-details-page', 'location-details-page']

        photoGroups = GroupView.get_photoGroup(request)
        presets = Presets.objects.filter(Q(event_id=None)| Q(event_id=request.session['event_auth_user']['event_id']))
        current_language = LanguageView.get_current_preset(request)
        languages = Presets.objects.filter(Q(event_id=event_id) | Q(event_id=None))
        pdf_templates = EmailTemplates.objects.filter(category='pdf', is_show=1, event_id=event_id)
        # ErrorR.okblue("-------------------")
        # ErrorR.okblue(language)
        # ErrorR.okblue("////////////////////")
        rebates = Rebates.objects.values('name', 'id').filter(event_id=event_id)
        att_export_list = ExportRule.objects.filter(group__event_id=event_id).exclude(preset__icontains='hotel_view')

        context = {
            "content": content,
            "question_groups_json": json.dumps(question_groups),
            "question_groups": questionGroups,
            "questionGroups": questionGroups,
            "plugins": json.dumps(plugins),
            "static_page": static_page,
            "locationGroups": locationGroups,
            "sessionGroups": sessionGroups,
            "session_groups": session_groups,
            "hotelGroups": hotelGroups,
            "filterGroups": filterGroups,
            'filterGroup': filterGroups,
            'attendee_groups': attendee_groups,
            'tags': tags,
            "quick_filter_id": quick_filter_id,
            "filter_groups": json.dumps(filter_groups),
            "language": language,
            "request": request,
            "element_settings": json.dumps(element_settings_dict),
            "element_settings_title": json.dumps(element_settings_title_dict),
            "class_list": class_list,
            "all_pages": all_pages,
            "emails": emails,
            "messages": messages,
            "static_url": settings.STATIC_URL_ALT,
            "pages": pages,
            "plugin_settings": plugin_settings,
            "exclude_form_pages": exclude_form_pages,
            "photoGroups": photoGroups,
            "presets":presets,
            "current_language":current_language,
            "rebates":rebates,
            "att_export_list":att_export_list,
            "pdf_templates":pdf_templates,
            "languages":languages
        }
        # get_files = FileView.get_all_files(request)
        # context['filelist'] = get_files['filelist']
        editor_common_context = EditorHelper.get_editor_context(request, styles=True, min_height=300, max_height=300, toolbar_inline=1)
        context.update(editor_common_context)
        # return render_to_string('page/cms_page.html', context)
        return render_to_string('page/cms_page_new.html', context)

    def get_treeView_question_group(request):
        questionGroup = GroupView.get_questionGroup(request)
        question_groups = []
        for group in questionGroup:
            group_dict = {}
            group_dict['text'] = group.name.title()
            group_dict['spriteCssClass'] = "folder"
            group_dict['gp_data_id'] = group.id
            questions = []
            group.questions = Questions.objects.all().filter(group_id=group.id).order_by('question_order')
            group.column_questions = group.questions
            for question in group.questions:
                is_default = 0
                if question.actual_definition:
                    is_default = 1
                question_dict = {}
                question_dict['text'] = question.title.title()
                question_dict['spriteCssClass'] = "question"
                question_dict['data_id'] = question.id
                question_dict['is_default'] = is_default
                questions.append(question_dict)
            group_dict['items'] = questions
            question_groups.append(group_dict)
        if len(question_groups) > 0:
            question_groups[0]['expanded'] = True
        return question_groups

    def get_fancyTreeView_question_group(request):
        event_id = request.session['event_auth_user']['event_id']
        questionGroup = GroupView.get_questionGroup(request)
        question_groups = []
        try:
            selectedValue = Setting.objects.filter(name='attendee_global_settings', event_id=event_id).first().value
            json_data = json.loads(eval(selectedValue))
            question_ids = json_data['question'][0]['id'].split(',')
        except:
            question_ids = []
        for group in questionGroup:
            group_dict = {}
            group_dict['title'] = group.name.title()
            group_dict['data_id'] = group.id
            group_dict['folder'] = True
            questions = []
            group.questions = Questions.objects.all().filter(group_id=group.id).order_by('question_order')
            group.column_questions = group.questions
            for question in group.questions:
                question_dict = {}
                question_dict['title'] = question.title.title()
                question_dict['data_id'] = question.id
                if str(question.id) in question_ids:
                    question_dict['selected'] = True
                question_dict['folder'] = False
                questions.append(question_dict)
            group_dict["children"] = questions
            question_groups.append(group_dict)
        return question_groups

    def replace_questions(request,pageContent,language_id):
        try:
            questions = []
            match = re.findall("questionid:\d+,box:\d+", pageContent)
            for q in match:
                question_data = q.split(',')
                qids = question_data[0]
                box = question_data[1]
                data = {
                    'qid': qids.split(':')[1],
                    'box_id': str(box.split(":")[1])
                }
                questions.append(data)
            request.session['event_id'] = request.session['event_auth_user']['event_id']
            if language_id == None:
                current_language = Presets.objects.get(id=6)
                language_id = current_language.preset.id
            select_text = LanguageKey.catch_lang_key(request, "questions","th_question_select_option")
            for qid in questions:
                try:
                    question = Questions.objects.get(id=qid['qid'])
                    question = LanguageElement.get_question_with_language(request,question,language_id)
                    options = Option.objects.filter(question_id=qid['qid'])
                    slug_title = slugify(question.title)
                    description = ''
                    # if question.description != '' and question.description != None:
                    if question.show_description:
                        description = """<span class="event-question-label-description">""" + question.description + """</span>"""
                    if question.type == 'select':
                        option = """<option value="">- {} -</option>""".format(select_text)
                        for opt in options:
                            opt = LanguageElement.get_option_with_language(request,opt,language_id)
                            option += """<option value='""" + opt.option + """'>""" + opt.option + """</option>"""
                        content = """<label for="attendee-question-""" + str(
                            question.id) + """" class="event-question-label">""" + question.title + description + """</label>
                                <div class="event-plugin-select">
                                <select id="attendee-question-""" + str(question.id) + """" class="given-answer">
                                """ + option + """
                                </select>
                                </div>"""
                    elif question.type == 'radio_button':
                        option = ""
                        for key, opt in enumerate(options):
                            counter = key + 1
                            opt = LanguageElement.get_option_with_language(request,opt,language_id)
                            option += """<div class="radio-wrapper"><input type="radio" name="attendee-question-""" + str(
                                question.id) + """" value='""" + opt.option + """' id="attendee-question-""" + str(
                                question.id) + """-""" + str(
                                counter) + """" class="given-answer"><label for="attendee-question-""" + str(
                                question.id) + """-""" + str(
                                counter) + """" class="radio-label">""" + opt.option + """</label></div>"""
                        content = """<label class="event-question-label">""" + question.title + description + """</label>
                                """ + """<div class="event-question-radio">""" + option + """</div>"""
                    elif question.type == 'text':
                        content = """<label for="attendee-question-""" + str(
                            question.id) + """" class="event-question-label">""" + question.title + description + """</label>
                                  <input type="text" id="attendee-question-""" + str(
                            question.id) + """" class="given-answer">"""
                    elif question.type == 'checkbox':
                        option = ""
                        for key, opt in enumerate(options):
                            counter = key + 1
                            opt = LanguageElement.get_option_with_language(request,opt,language_id)
                            option += """<div class="checkbox-wrapper"><input class="given-answer" type="checkbox" name="attendee-question-""" + str(
                                question.id) + """" value=""" + opt.option + """ id="attendee-question-""" + str(
                                question.id) + """-""" + str(counter) + """"><label for="attendee-question-""" + str(
                                question.id) + """-""" + str(
                                counter) + """" class="checkbox-label">""" + opt.option + """</label></div>"""
                            content = """<label for="attendee-""" + slug_title + """" class="event-question-label">""" + question.title + description + """</label>
                                """ + """<div class="event-question-checkbox">""" + option + """</div>"""
                    elif question.type == 'textarea':
                        content = """<label for="attendee-question-""" + str(
                            question.id) + """" class="event-question-label">""" + question.title + description + """</label>
                                  <textarea id="attendee-question-""" + str(
                            question.id) + """" class="given-answer"></textarea>"""
                    elif question.type=='date':
                        content = """<label for="attendee-question-""" + str(
                            question.id) + """" class="event-question-label">""" + question.title + description + """</label>
                                                          <input type="text" class="given-answer">"""
                    elif question.type=='time':
                        content = """<label for="attendee-question-""" + str(
                            question.id) + """" class="event-question-label">""" + question.title + description + """</label>
                                                          <input type="text" class="given-answer">"""
                    elif question.type=='date_range':
                        content = """<label for="attendee-question-""" + str(question.id) + """" class="event-question-label">""" + question.title + description + """</label>
                            <div style="overflow:hidden">
                            <input style="width:50%; display:inline; float:left" type="text"  class="given-answer">
                            <input style="width:50%; display:inline; float:left" type="text"  class="given-answer"></div>"""
                    elif question.type=='time_range':
                        content = """<label for="attendee-question-""" + str(question.id) + """" class="event-question-label">""" + question.title + description + """</label>
                            <div style="overflow:hidden">
                            <input style="width:50%; display:inline; float:left" type="text" class="given-answer">
                            <input style="width:50%; display:inline; float:left" type="text" class="given-answer"></div>"""
                    elif question.type == 'country':
                        option = """<option value="">- {} -</option>""".format(select_text)
                        content = """<label for="attendee-question-""" + str(
                            question.id) + """" class="event-question-label">""" + question.title + description + """</label>
                                <div class="event-plugin-select">
                                <select id="attendee-question-""" + str(question.id) + """" class="event-question-country given-answer">
                                """ + option + """
                                </select>
                                </div>"""
                    else:
                        content = """<label for="attendee-question-""" + str(
                            question.id) + """" class="event-question-label">""" + question.title + description + """</label>
                                  <input type="text" id="attendee-question-""" + str(
                            question.id) + """" class="given-answer">"""

                    box_data = "box-"+qid["box_id"]
                    required = ""
                    question_required = 0
                    actual_def = "null"
                    if question.required:
                        question_required = 1
                        required = " required"
                    if question.actual_definition:
                        actual_def = str(question.actual_definition)
                    element = """<div class="event-question element box""" + required + """" data-id=""" + str(question.id) + """ data-req=""" + str(question_required) + """ data-def=""" + actual_def + """ id=""" + box_data + """ type=""" + question.type + """>"""+\
                              content + """<div class="error-on-validate">Please select your '""" + question.title + """'</div></div>"""
                    pageContent = pageContent.replace('{questionid:' + qid['qid'] + ',box:' + qid['box_id'] + '}', element)
                except Exception as e:
                    ErrorR.efail(e)
                    pageContent = pageContent.replace('{questionid:' + qid['qid'] + ',box:' + qid['box_id'] + '}', "")
            return pageContent
        except Exception as e:
            ErrorR.efail(e)
            return pageContent

    def get_page(request, pk):
        staticPage = PageContent.objects.get(pk=pk)
        page_groups = PagePermission.objects.filter(page_id=staticPage.id)
        groups = []
        for group in page_groups:
            group_data = {}
            if group.rule:
                group_data['id'] = group.rule.id
                group_data['text'] = group.rule.name
                groups.append(group_data)
        response = {
            'success': True,
            'page': staticPage.as_dict(),
            'groups': groups
        }
        return HttpResponse(json.dumps(response), content_type='application/json')

    def get_all_menu(request, mainMenu, language_id):
        for menu in mainMenu:
            menu_id = menu.id
            menu_items = MenuItem.objects.filter(parent_id=menu_id,is_visible=1).order_by('rank')
            menu.items=[]
            if menu.title_lang != '' and menu.title_lang != None:
                try:
                    menu_title_lang = json.loads(menu.title_lang, strict=False)
                    if menu_title_lang[str(language_id)]:
                        menu.title = menu_title_lang[str(language_id)]
                except Exception as e:
                    pass
            for m in menu_items:
                menu.items.extend(MenuItem.objects.filter(id=m.id))
            for item in menu.items:
                item_id = item.id
                menu_items = MenuItem.objects.filter(parent_id=item_id,is_visible=1).order_by('rank')
                item.items=[]
                if item.title_lang != '' and item.title_lang != None:
                    try:
                        item_title_lang = json.loads(item.title_lang, strict=False)
                        if item_title_lang[str(language_id)]:
                            item.title = item_title_lang[str(language_id)]
                    except Exception as e:
                        pass
                for m in menu_items:
                    item.items.extend(MenuItem.objects.filter(id=m.id))
                if len(item.items) > 0:
                    PageDetailView.get_all_menu(request, item.items, language_id)
        return mainMenu

    def get_all_language(request):
        event_id = request.session["event_auth_user"]["event_id"]
        languages= Presets.objects.filter(Q(event_id=event_id) | Q(event_id=None))
        for language in languages:
            language.preset_class = slugify(language.preset_name.lower())
        try:
            current_language = PresetEvent.objects.filter(event_id=event_id).first()
            current_language.id = current_language.preset.id
            current_language.preset_name = current_language.preset.preset_name
            current_language.preset_class = slugify(current_language.preset_name.lower())
        except:
            current_language = Presets.objects.get(id=6)
            current_language.preset_class = slugify(current_language.preset_name.lower())
        context = {
            'request': request,
            'languages': languages,
            "current_language": current_language
        }
        return render_to_string('content/cms_language.html',context)

    def replace_plugin(request, pageContent):
        try:
            plugins = re.findall("element:[^,(?! )]+,box:\d+,button_id:\d+|element:[^,(?! )]+,box:\d+", pageContent)
            for plugin in plugins:
                plugin_data = plugin.split(",")
                element = plugin_data[0]
                box = plugin_data[1]
                element_plugin = element.split(":")[1]
                box_id = box.split(":")[1]
                plugin_info = Elements.objects.get(slug=element_plugin)
                if element_plugin == 'submit-button':
                    button_info = plugin_data[2]
                    button_id = button_info.split(":")[1]
                    submit_button = PluginSubmitButton.objects.get(id=int(button_id))
                    plugin_html = """<div class="event-plugin element event-plugin-"""+element_plugin+""" box" id="box-"""+str(box_id)+"""" data-id="""+str(plugin_info.id)+""" data-name="""+element_plugin+""" data-submit-id="""+str(submit_button.id)+""" data-submit-name="""+submit_button.name+"""></div>"""
                elif element_plugin == 'photo-upload':
                    button_info = plugin_data[2]
                    button_id = button_info.split(":")[1]
                    photo_group = PhotoGroup.objects.get(id=int(button_id))
                    plugin_html = """<div class="event-plugin element event-plugin-"""+element_plugin+""" box" id="box-"""+str(box_id)+"""" data-id="""+str(plugin_info.id)+""" data-name="""+element_plugin+""" data-photo-group-id="""+str(photo_group.id)+""" data-photo-group-name="""+photo_group.name+"""></div>"""
                elif element_plugin == 'pdf-button':
                    button_info = plugin_data[2]
                    button_id = button_info.split(":")[1]
                    pdf_button = PluginPdfButton.objects.get(id=int(button_id))
                    plugin_html = """<div class="event-plugin element event-plugin-""" + element_plugin + """ box" id="box-""" + str(box_id) + """" data-id=""" + str(plugin_info.id) + """ data-name=""" + element_plugin + """ data-pdf-button-id=""" + str(pdf_button.id) + """ data-pdf-button-name=""" + pdf_button.name + """></div>"""
                else:
                    plugin_html = """<div class="event-plugin element event-plugin-"""+element_plugin+""" box" id="box-"""+str(box_id)+"""" data-id="""+str(plugin_info.id)+""" data-name="""+element_plugin+"""></div>"""
                pageContent = pageContent.replace('{' + plugin + '}', plugin_html)
            return pageContent
        except Exception as e:
            ErrorR.efail(e)
            return pageContent

    def page_duplicate(request):
        response_data = {}
        try:
            event_id = request.session['event_auth_user']['event_id']
            if EventView.check_permissions(request, 'page_permission'):
                page_id = request.POST.get('page_id')
                page = PageContent.objects.get(id=page_id, event_id=event_id)

                duplicate_existance = PageContent.objects.filter(url=page.url + '-copy', event_id=event_id)
                if duplicate_existance.exists():
                    response_data['error'] = 'This Page is already make a duplicate.'
                    return HttpResponse(json.dumps(response_data), content_type='application/json')
                current_admin_id = int(request.session['event_auth_user']['id'])
                page_form = {
                    "url": page.url+'-copy',
                    "login_required": page.login_required,
                    "disallow_logged_in": page.disallow_logged_in,
                    "content": page.content,
                    "filter": page.filter,
                    "element_filter": page.element_filter,
                    "created_by_id": current_admin_id,
                    "last_updated_by_id": current_admin_id,
                    "template_id": page.template_id,
                    "event_id": page.event_id
                }
                new_page = PageContent(**page_form)
                new_page.save()
                exclude_plugin_settings = ['location_location_groups', 'session_radio_session_groups',
                                           'session_checkbox_session_groups', 'submit_button_redirect_page',
                                           'submit_button_email_send']
                page_element_answers = ElementsAnswers.objects.filter(page_id=page_id).exclude(
                    element_question__question_key__in=exclude_plugin_settings)
                element_settings = []
                for element_answers in page_element_answers:
                    element_answers_dict = {
                        "answer": element_answers.answer,
                        "description": element_answers.description,
                        "box_id": element_answers.box_id,
                        "created_by_id": current_admin_id,
                        "last_updated_by_id": current_admin_id,
                        "element_question_id": element_answers.element_question_id,
                        "page_id": new_page.id
                    }
                    element_answer_data = ElementsAnswers(**element_answers_dict)
                    element_settings.append(element_answer_data)
                ElementsAnswers.objects.bulk_create(element_settings)
                element_classes = PageContentClasses.objects.filter(page_id=page.id)
                element_class_list = []
                for element_class in element_classes:
                    element_class_dict = {
                        "box_id": element_class.box_id,
                        "classname_id": element_class.classname_id,
                        "page_id": new_page.id
                    }
                    element_classes_data = PageContentClasses(**element_class_dict)
                    element_class_list.append(element_classes_data)
                PageContentClasses.objects.bulk_create(element_class_list)
                custom_elements = ElementHtml.objects.filter(page_id=page_id)
                custom_elements_list = []
                for custom_element in custom_elements:
                    custom_element_form = {
                        "box_id": custom_element.box_id,
                        "compiled": custom_element.compiled,
                        "uncompiled": custom_element.uncompiled,
                        "created_by_id": current_admin_id,
                        "language_id": custom_element.language_id,
                        "page_id": new_page.id
                    }
                    custom_element_data = ElementHtml(**custom_element_form)
                    custom_elements_list.append(custom_element_data)
                ElementHtml.objects.bulk_create(custom_elements_list)
                page_permissions = PagePermission.objects.filter(page_id=page_id)
                page_permissions_list = []
                for page_permission in page_permissions:
                    page_permission_form = {
                        "page_id": new_page.id,
                        "rule_id": page_permission.rule_id
                    }
                    page_permission_data = PagePermission(**page_permission_form)
                    page_permissions_list.append(page_permission_data)
                PagePermission.objects.bulk_create(page_permissions_list)
                response_data['success'] = "Create duplicate Page Successfully"
                response_data['page'] = {
                    "id": new_page.id,
                    "url": new_page.url
                }
            else:
                response_data['error'] = 'You do not have Permission to do this'
        except Exception as e:
            ErrorR.efail(e)
            response_data['error'] = 'Something went wrong. Please try again.'
        return HttpResponse(json.dumps(response_data), content_type='application/json')


class LanguageElement(generic.DetailView):

    def get_cms_pag_with_language(request):
        page_id= request.POST.get('page_id')
        language_id = request.POST.get('language_id')
        response_data = {}
        try:
            event_id = request.session['event_auth_user']['event_id']
            try:
                page = PageContent.objects.filter(id=page_id,template__event_id=event_id)
                if page.exists():
                    static_page = page[0]
                else:
                    raise Http404
            except PageContent.DoesNotExist:
                raise Http404
            first_level_menu = MenuItem.objects.filter(level=1, event_id=static_page.template.event_id).order_by("rank")
            all_menus = PageDetailView.get_all_menu(request,first_level_menu, language_id)
            menu = render_to_string('content/cms_menu.html',{"all_menu": all_menus})
            content = LanguageElement.replace_page_content(request,static_page,language_id)
            element_settings_dict = LanguageElement.get_element_settings_data(request,static_page,language_id)
            element_title_settings_dict = LanguageElement.get_element_title_settings_data(request,static_page,language_id)
            language = {}
            modules = Elements.objects.all().exclude(type="public_notification")
            plugin_settings = {}
            for module in modules:
                plugin_slug = module.slug.replace("-", "_")
                lang_data = ElementPresetLang.objects.filter(preset_id=language_id,
                                                             element_default_lang__element_id=module.id)
                lang_key = {}
                for lang in lang_data:
                    lang_key[lang.element_default_lang.lang_key] = lang.value

                language[plugin_slug] = lang_key
                module_settings = ElementsQuestions.objects.filter(group_id=module.id)
                module_key = {}
                for module_setting in module_settings:
                    module_key[module_setting.question_key] = module_setting
                plugin_settings[plugin_slug] = module_key
            class_list = LanguageElement.get_page_classes(request,static_page)
            context = {
                "language" : language,
                "plugin_settings" : plugin_settings
            }
            all_plugins = render_to_string('page/plugins.html',context)
            response_data['content'] = content
            response_data['element_settings'] = json.dumps(element_settings_dict),
            response_data['element_title_settings'] = json.dumps(element_title_settings_dict),
            response_data['class_list'] = json.dumps(class_list)
            response_data['menu'] = menu
            response_data['all_plugins'] = all_plugins
            response_data['success'] = True
        except Exception as e:
            ErrorR.efail(e)
            response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_question_with_language(request, question, language_id):
        if question.title_lang != '' and question.title_lang != None:
            try:
                question_title_lang = json.loads(question.title_lang, strict=False)
                if question_title_lang[str(language_id)]:
                    question.title = question_title_lang[str(language_id)]
            except:
                pass
        if question.description_lang != '' and question.description_lang != None:
            try:
                question_description_lang = json.loads(question.description_lang, strict=False)
                if question_description_lang[str(language_id)]:
                    question.description = question_description_lang[str(language_id)]
            except:
                pass
        return question

    def get_option_with_language(request, option, language_id):
        if option.option_lang != '' and option.option_lang != None:
            try:
                option_lang = json.loads(option.option_lang, strict=False)
                if option_lang[str(language_id)]:
                    option.option = option_lang[str(language_id)]
            except:
                pass
        return option

    def replace_page_content(request, static_page, language_id):

        css_version_obj = StyleSheet.objects.get(event_id=request.session['event_auth_user']['event_id'])
        css_version = css_version_obj.version

        pageContent = static_page.content
        pageContent = CmsPageView.replace_section(request,pageContent,static_page.id)
        pageContent = CmsPageView.replace_row(request,pageContent,static_page.id)
        pageContent = CmsPageView.replace_col(request,pageContent,static_page.id)
        pageContent = CmsPageView.replace_editor_html(request,pageContent,static_page.id,language_id)
        pageContent = PageDetailView.replace_questions(request, pageContent, language_id)
        pageContent = PageDetailView.replace_plugin(request, pageContent)
        pageContent = CmsPageView.replace_enddiv(request,pageContent)
        # For Wsit S3
        content = pageContent.replace('[[file]]', "[[static]]public/[[event_url]]/files")
        content = content.replace('[[files]]', "[[static]]public/[[event_url]]/files/")
        content = content.replace('[[css]]', "[[static]]public/[[event_url]]/compiled_css/style.css?v="+str(css_version))

        # For Wsit Event
        # content = pageContent.replace('[[file]]', "[[static]]public/files")
        # content = content.replace('[[files]]', "[[static]]public/files/")
        # content = content.replace('[[css]]',
        #                           "[[static]]public/compiled_css/main_style.css?v=" + str(css_version))

        content = content.replace('[[static]]', settings.STATIC_URL_ALT)
        return content

    def get_element_settings_data(request,static_page,language_id):
        element_settings = ElementsAnswers.objects.filter(page_id=static_page.id).select_related('element_question').select_related('element_question__group')
        element_settings_dict = []
        for setting in element_settings:
            new_setting_data = {}
            new_setting_data['answer'] = setting.answer
            # if setting.description != "":
            #     try:
            #         msg = json.loads(setting.description,strict=False)
            #         setting.description = msg[str(language_id)]
            #     except Exception as e:
            #         ErrorR.efail(e)
            #         try:
            #             current_language = LanguageView.get_current_preset(request)
            #             setting.description = msg[str(current_language.preset_id)]
            #         except:
            #             setting.description = ""
            # if setting.element_question.question_key == "submit_button_title" or setting.element_question.question_key == "pdf_button_title":
            #     title_new = ''
            #     if setting.answer != '':
            #         try:
            #             title = json.loads(setting.answer,strict=False)
            #             if title[str(language_id)]:
            #                 title_new = title[str(language_id)]
            #         except ValueError:
            #             title_new = setting.answer
            #         except Exception as e:
            #             try:
            #                 current_language = LanguageView.get_current_preset(request)
            #                 title = json.loads(setting.answer,strict=False)
            #                 if title[str(current_language.preset_id)]:
            #                     title_new = title[str(current_language.preset_id)]
            #             except:
            #                 pass
            #     new_setting_data['answer'] = title_new
            # new_setting_data['description'] = setting.description
            new_setting_data['box_id'] = setting.box_id
            new_setting_data['element_question'] = {
                "id": setting.element_question.id,
                "group_slug": setting.element_question.group.slug,
                "question_key": setting.element_question.question_key
            }
            # new_setting_data['element_question'] = setting.element_question.as_dict()
            element_settings_dict.append(new_setting_data)
        return element_settings_dict

    def get_element_title_settings_data(request, static_page, language_id):
        question_keys = ['submit_button_title','pdf_button_title']
        element_settings = ElementsAnswers.objects.filter(page_id=static_page.id, element_question__question_key__in=question_keys).select_related('element_question').select_related('element_question__group')
        element_settings_dict = []
        for setting in element_settings:
            new_setting_data = {}
            title_new = ''
            if setting.answer != '':
                try:
                    title = json.loads(setting.answer, strict=False)
                    if title[str(language_id)]:
                        title_new = title[str(language_id)]
                except ValueError:
                    title_new = setting.answer
                except Exception as e:
                    try:
                        current_language = LanguageView.get_current_preset(request)
                        title = json.loads(setting.answer, strict=False)
                        if title[str(current_language.preset_id)]:
                            title_new = title[str(current_language.preset_id)]
                    except:
                        pass
            new_setting_data['answer'] = title_new
            new_setting_data['box_id'] = setting.box_id
            new_setting_data['element_question'] = {
                "id": setting.element_question.id,
                "group_slug": setting.element_question.group.slug,
                "question_key": setting.element_question.question_key
            }
            # new_setting_data['element_question'] = setting.element_question.as_dict()
            element_settings_dict.append(new_setting_data)
        return element_settings_dict

    def get_page_classes(request, static_page):
        page_classes = PageContentClasses.objects.filter(page_id=static_page.id)
        class_list = []
        for page_class in page_classes:
            box_class = {"box_id": page_class.box_id, "class_name": page_class.classname.classname}
            class_list.append(box_class)
        return class_list
